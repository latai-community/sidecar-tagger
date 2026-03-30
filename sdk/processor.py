"""
Title: Metadata Processor Core (v2)
Abstract: Orchestrates the 4-Layer Pipeline (Hash -> Native+OS -> Embeddings -> LLM).
Dependencies: os, json, logging, sdk.parsers, sdk.llm_client, sdk.embeddings_client, sdk.exceptions, sdk.utils.hashing, sdk.context
LLM-Hints: This is the brain of the system.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

from sdk.config import ProcessorConfig, AnalysisLevel
from sdk.models.metadata import FileMetadata, LocalContext, ClusterHint
from sdk.parsers import PdfParser, XlsxParser, ImageParser, TxtParser
from sdk.llm_client import LLMClient
from sdk.embeddings_client import LocalEmbeddings
from sdk.exceptions import SidecarException, ParserError, LLMClientError, CacheError
from sdk.utils.hashing import calculate_sha256
from sdk.context.os_extractor import OSContextExtractor
from sdk.context.clustering import ClusterManager

# Configuration for Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("SidecarProcessor")

class MetadataProcessor:
    """
    Orchestrates the 4-Layer Pipeline:
    - Layer 0: Hash Dedup
    - Layer 1: Native + OS Metadata
    - Layer 2: Embeddings (Semantic Cache)
    - Layer 3: LLM + Clustering Hint
    """

    def __init__(
        self, 
        config: Optional[ProcessorConfig] = None,
        output_path: Optional[str] = None,
        similarity_threshold: Optional[float] = None
    ) -> None:
        # Use config or create default
        self.config = config or ProcessorConfig()
        
        # Allow override of config values via constructor args (backward compatibility)
        if output_path:
            self.config.output_path = output_path
        if similarity_threshold is not None:
            self.config.layer_2_similarity_threshold = similarity_threshold
        
        # Core Components
        self.metadata_store: Dict[str, Dict[str, Any]] = self._load_existing_store()
        self.hash_index: Dict[str, str] = self._build_hash_index() # Maps hash -> file_path
        
        self.llm_client = LLMClient()
        self.embeddings_client = LocalEmbeddings()
        self.os_extractor = OSContextExtractor()
        self.cluster_manager = ClusterManager()
        
        # Parser Registry
        self._parsers = {
            ".pdf": PdfParser(),
            ".xlsx": XlsxParser(),
            ".xls": XlsxParser(),
            ".txt": TxtParser(),
            ".md": TxtParser(),
            ".log": TxtParser(),
            ".jpg": ImageParser(),
            ".jpeg": ImageParser(),
            ".png": ImageParser(),
            ".webp": ImageParser(),
            ".bmp": ImageParser()
        }

    def _load_existing_store(self) -> Dict[str, Any]:
        if not os.path.exists(self.config.output_path):
            return {}
        try:
            with open(self.config.output_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load store: {e}")
            return {}

    def _build_hash_index(self) -> Dict[str, str]:
        """Builds an index of {sha256: file_path} from existing metadata for Layer 0."""
        index = {}
        for path, meta in self.metadata_store.items():
            file_hash = meta.get("file_hash")
            if file_hash:
                index[file_hash] = path
        return index

    def _find_similar_vector(self, current_vector: List[float]) -> Optional[Dict[str, Any]]:
        """Layer 2: Semantic Cache Check."""
        for path, metadata in self.metadata_store.items():
            stored_vector = metadata.get("embedding_vector")
            if stored_vector:
                try:
                    similarity = self.embeddings_client.calculate_similarity(current_vector, stored_vector)
                    if similarity >= self.config.layer_2_similarity_threshold:
                        logger.info(f" -> Layer 2 Hit: Semantic Match with {path} ({similarity:.2f})")
                        cached = metadata.copy()
                        cached["confidence"] = similarity
                        # We keep original context/tags but might want to mark it as derived
                        return cached
                except CacheError:
                    continue
        return None

    def process_files(self, file_paths: List[str]) -> None:
        """Main batch processing loop."""
        
        # Layer 1.5: Pre-calculate clustering hints
        logger.info(" -> Layer 1.5: Analyzing file clusters...")
        self.cluster_manager.analyze_neighborhood(file_paths)
        
        for path in file_paths:
            if os.path.isfile(path):
                try:
                    metadata = self.extract_metadata(path)
                    self.metadata_store[path] = metadata
                    
                    # Update hash index immediately for subsequent duplicates in the same batch
                    if metadata.get("file_hash"):
                        self.hash_index[metadata["file_hash"]] = path
                        
                except Exception as e:
                    logger.error(f"Failed to process {path}: {e}")
                    self.metadata_store[path] = self._get_error_metadata(str(e))
            else:
                logger.warning(f"Skipping invalid path: {path}")

        self.save_sidecar()

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        The 4-Layer Pipeline Implementation.
        Respects config to determine which layers to execute.
        
        Returns a dict with 'layers' key indicating which layers were processed.
        """
        
        filename = os.path.basename(file_path)
        logger.info(f"Processing: {filename}")
        
        # Track which layers were executed
        layers_processed = []

        try:
            # --- LAYER 0: Binary Identity (Hash Gate) ---
            if self.config.use_layer_0:
                file_hash = calculate_sha256(file_path)
                if file_hash in self.hash_index:
                    original_path = self.hash_index[file_hash]
                    logger.info(f" -> Layer 0 Hit: Exact duplicate of {original_path}")
                    
                    # Clone metadata from original
                    original_meta = self.metadata_store.get(original_path, {}).copy()
                    original_meta["file_hash"] = file_hash
                    original_meta["duplicate_of"] = original_path
                    # Update local context for the duplicate (it has its own path/dates)
                    original_meta["local_context"] = self.os_extractor.extract(file_path).model_dump()
                    original_meta["layers"] = ["0"]
                    
                    return original_meta
                
                layers_processed.append(0)
            else:
                file_hash = None

            # --- LAYER 1: Native + OS Metadata ---
            if self.config.use_layer_1:
                local_context = self.os_extractor.extract(file_path)
                
                # Check confidence from native metadata (if available)
                confidence = self._calculate_layer1_confidence(local_context)
                
                # Layer 1 shortcut: if confidence >= threshold, return early
                if confidence >= self.config.layer_1_confidence_threshold:
                    logger.info(f" -> Layer 1 Shortcut: Confidence {confidence:.2f} >= {self.config.layer_1_confidence_threshold}")
                    result = {
                        "file_hash": file_hash,
                        "doc_type": local_context.file_extension,
                        "tags": self._extract_tags_from_context(local_context),
                        "confidence": confidence,
                        "local_context": local_context.model_dump(),
                        "source": "layer_1",
                        "layers": layers_processed + [1]
                    }
                    return result
                
                layers_processed.append(1)
            else:
                # Layer 1 disabled - create minimal context
                local_context = None

            # Get clustering hint (used by Layer 3 if enabled)
            cluster_hint = self.cluster_manager.get_hint(file_path)
            if cluster_hint.cluster_id:
                logger.info(f" -> Layer 1.5 Hint: Member of {cluster_hint.cluster_id} (Sim: {cluster_hint.similarity_score:.2f})")

            # Initialize content variables (needed for Layer 2 and/or Layer 3)
            content = ""
            image_to_send = None
            ext = ""
            
            # Extract Content (needed for Layer 2 and/or Layer 3)
            if self.config.use_layer_2 or self.config.use_layer_3:
                if local_context is None:
                    local_context = self.os_extractor.extract(file_path)
                
                ext = local_context.file_extension
                
                parser = self._parsers.get(ext)
                if parser:
                    res = parser.extract(file_path)
                    content = res.get("text", "")
                    image_to_send = res.get("thumbnail_path")
                else:
                    content = f"Generic content for {filename}"

            # --- LAYER 2: Embeddings (Semantic Cache) ---
            if self.config.use_layer_2:
                # Ensure we have local_context
                if local_context is None:
                    local_context = self.os_extractor.extract(file_path)
                
                # Generate vector using content + context hints
                parent = local_context.parent_folder if local_context else ""
                vector_content = content if content.strip() else f"{filename} {parent}"
                vector = self.embeddings_client.generate_vector(vector_content)
                
                cached_meta = self._find_similar_vector(vector)
                if cached_meta:
                    self._cleanup(image_to_send, ext)
                    cached_meta["file_hash"] = file_hash
                    cached_meta["local_context"] = local_context.model_dump()
                    cached_meta["cluster_hint"] = cluster_hint.model_dump()
                    cached_meta["embedding_vector"] = vector
                    cached_meta["layers"] = layers_processed + [2]
                    return cached_meta
                
                layers_processed.append(2)
            else:
                vector = None

            # --- LAYER 3: LLM + Clustering Hint ---
            if self.config.use_layer_3:
                logger.info(f" -> Layer 3: Deep Analysis with Gemini...")
                
                # Ensure we have local_context for LLM
                if local_context is None:
                    local_context = self.os_extractor.extract(file_path)
                
                # Inject Context into LLM Client
                pdf_path = file_path if ext == ".pdf" else None
                
                metadata = self.llm_client.generate_metadata(
                    content=content,
                    image_path=image_to_send,
                    pdf_path=pdf_path,
                    local_context=local_context,
                    cluster_hint=cluster_hint
                )
                
                # Merge Results
                result = metadata.model_dump(mode='json')
                result["file_hash"] = file_hash
                result["embedding_vector"] = vector
                result["local_context"] = local_context.model_dump()
                result["cluster_hint"] = cluster_hint.model_dump()
                result["layers"] = layers_processed + [3]

                self._cleanup(image_to_send, ext)
                return result

            # If we got here without hitting any layer that returns, return minimal metadata
            return {
                "file_hash": file_hash,
                "doc_type": "unknown",
                "tags": [],
                "confidence": 0.0,
                "layers": layers_processed
            }

        except (ParserError, LLMClientError, CacheError) as e:
            logger.error(f"Failed to process {filename}: {str(e)}")
            return self._get_error_metadata(str(e))
        except Exception as e:
            logger.critical(f"Unexpected system error processing {filename}: {str(e)}")
            return self._get_error_metadata(f"Internal Error: {str(e)}")
    
    def _calculate_layer1_confidence(self, local_context: LocalContext) -> float:
        """
        Calculate confidence score based on available Layer 1 metadata.
        This is a simplified version - full implementation would use EXIFTOOL.
        """
        score = 0.0
        
        # Check internal_props for author/title (from file headers)
        if local_context.internal_props:
            if local_context.internal_props.get("Author") and local_context.internal_props.get("Title"):
                score += 0.5
            elif local_context.internal_props.get("Author") or local_context.internal_props.get("Title"):
                score += 0.25
            
            if local_context.internal_props.get("Keywords") or local_context.internal_props.get("Subject"):
                score += 0.2
        
        # Check path keywords
        if local_context.path_keywords:
            score += 0.1
        
        # Check if we have meaningful filename (not generic)
        if local_context.filename and len(local_context.filename) > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _extract_tags_from_context(self, local_context: LocalContext) -> list[str]:
        """Extract tags from Layer 1 metadata."""
        tags = []
        
        if local_context.internal_props:
            # Add author if present
            if local_context.internal_props.get("Author"):
                tags.append(local_context.internal_props["Author"])
            
            # Add keywords if present
            keywords = local_context.internal_props.get("Keywords", "")
            if keywords:
                if isinstance(keywords, str):
                    tags.extend([t.strip() for t in keywords.split(",")])
        
        # Add path keywords
        if local_context.path_keywords:
            tags.extend(local_context.path_keywords[:5])  # Limit to 5
        
        return list(set(tags))

    def save_sidecar(self) -> None:
        try:
            with open(self.config.output_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata_store, f, indent=4)
            logger.info(f"Saved manifest to {self.config.output_path}")
        except Exception as e:
            logger.error(f"Save failed: {e}")

    def _cleanup(self, img: Optional[str], ext: str) -> None:
        """Helper to remove temporary files."""
        if img and ext == ".pdf" and os.path.exists(img):
            try:
                os.remove(img)
            except: pass

    def _get_error_metadata(self, msg: str) -> Dict[str, Any]:
        """Helper to generate structured error response."""
        return {
            "doc_type": "error",
            "context": f"Failed: {msg}",
            "needs_review": True,
            "tags": ["error"],
            "confidence": 0.0
        }
