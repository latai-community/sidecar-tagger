"""
Title: Metadata Processor Core (v2)
Abstract: Orchestrates the 5-Layer Contextual Engine (Hash -> Context -> Cluster -> Embedding -> AI).
Dependencies: os, json, logging, sdk.parsers, sdk.llm_client, sdk.embeddings_client, sdk.exceptions, sdk.utils.hashing, sdk.context
LLM-Hints: This is the brain of the system.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

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
    Orchestrates the 5-Layer Contextual Engine.
    """

    def __init__(self, output_path: str = "sidecar.json", similarity_threshold: float = 0.9) -> None:
        self.output_path = output_path
        self.similarity_threshold = similarity_threshold
        
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
        if not os.path.exists(self.output_path):
            return {}
        try:
            with open(self.output_path, "r", encoding="utf-8") as f:
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
        """Layer 3: Semantic Cache Check."""
        for path, metadata in self.metadata_store.items():
            stored_vector = metadata.get("embedding_vector")
            if stored_vector:
                try:
                    similarity = self.embeddings_client.calculate_similarity(current_vector, stored_vector)
                    if similarity >= self.similarity_threshold:
                        logger.info(f" -> Layer 3 Hit: Semantic Match with {path} ({similarity:.2f})")
                        cached = metadata.copy()
                        cached["confidence"] = similarity
                        # We keep original context/tags but might want to mark it as derived
                        return cached
                except CacheError:
                    continue
        return None

    def process_files(self, file_paths: List[str]) -> None:
        """Main batch processing loop."""
        
        # Layer 2 Pre-calculation: Analyze neighborhood
        logger.info(" -> Layer 2: Analyzing file clusters...")
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
        """The 5-Layer Pipeline Implementation."""
        
        filename = os.path.basename(file_path)
        logger.info(f"Processing: {filename}")

        try:
            # --- LAYER 0: Binary Identity (Hash Gate) ---
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
                
                return original_meta

            # --- LAYER 1: Context Enrichment ---
            local_context = self.os_extractor.extract(file_path)
            
            # --- LAYER 2: Cluster Hint ---
            cluster_hint = self.cluster_manager.get_hint(file_path)
            if cluster_hint.cluster_id:
                 logger.info(f" -> Layer 2 Hint: Member of {cluster_hint.cluster_id} (Sim: {cluster_hint.similarity_score:.2f})")

            # Extract Content (Parsing)
            ext = local_context.file_extension
            content = ""
            image_to_send = None
            
            parser = self._parsers.get(ext)
            if parser:
                res = parser.extract(file_path)
                content = res.get("text", "")
                image_to_send = res.get("thumbnail_path")
            else:
                content = f"Generic content for {filename}"

            # --- LAYER 3: Semantic Identity ---
            # Generate vector using content + context hints
            # (For now we just embed content, v2.1 could embed context too)
            vector_content = content if content.strip() else f"{filename} {local_context.parent_folder}"
            vector = self.embeddings_client.generate_vector(vector_content)
            
            cached_meta = self._find_similar_vector(vector)
            if cached_meta:
                self._cleanup(image_to_send, ext)
                cached_meta["file_hash"] = file_hash
                cached_meta["local_context"] = local_context.model_dump()
                cached_meta["cluster_hint"] = cluster_hint.model_dump()
                cached_meta["embedding_vector"] = vector # Update vector just in case
                return cached_meta

            # --- LAYER 4: Cognitive Analysis (AI) ---
            logger.info(f" -> Layer 4: Deep Analysis with Gemini...")
            
            # Inject Context into LLM Client
            pdf_path = file_path if ext == ".pdf" else None
            
            metadata = self.llm_client.generate_metadata(
                content=content,
                image_path=image_to_send,
                pdf_path=pdf_path,
                local_context=local_context, # NEW
                cluster_hint=cluster_hint    # NEW
            )
            
            # Merge Results
            result = metadata.model_dump(mode='json')
            result["file_hash"] = file_hash
            result["embedding_vector"] = vector
            result["local_context"] = local_context.model_dump()
            result["cluster_hint"] = cluster_hint.model_dump()

            self._cleanup(image_to_send, ext)
            return result

        except (ParserError, LLMClientError, CacheError) as e:
            logger.error(f"Failed to process {filename}: {str(e)}")
            return self._get_error_metadata(str(e))
        except Exception as e:
            logger.critical(f"Unexpected system error processing {filename}: {str(e)}")
            return self._get_error_metadata(f"Internal Error: {str(e)}")

    def save_sidecar(self) -> None:
        try:
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata_store, f, indent=4)
            logger.info(f"Saved manifest to {self.output_path}")
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
