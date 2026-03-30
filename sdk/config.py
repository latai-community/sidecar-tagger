"""
Title: Configuration Module
Abstract: Defines analysis levels and processor configuration for the 4-Layer Pipeline.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class AnalysisLevel(Enum):
    """Available analysis depth levels."""
    MINIMAL = "minimal"   # Layer 0 only (hash dedup)
    FAST = "fast"         # Layer 0 + 1 (Native + OS)
    STANDARD = "standard" # Layer 0 + 1 + 2 (with semantic cache)
    DEEP = "deep"         # Layer 0 + 1 + 2 + 3 (full LLM analysis)


@dataclass
class ProcessorConfig:
    """
    Configuration for the MetadataProcessor.
    Controls which layers are enabled and their thresholds.
    """
    level: AnalysisLevel = AnalysisLevel.STANDARD
    
    # Layer 0: Hash Dedup (always enabled)
    use_layer_0: bool = True
    
    # Layer 1: Native + OS Metadata
    use_layer_1: bool = True
    layer_1_confidence_threshold: float = 0.8
    
    # Layer 2: Embeddings (Semantic Cache)
    use_layer_2: bool = True
    layer_2_similarity_threshold: float = 0.9
    
    # Layer 3: LLM + Clustering Hint
    use_layer_3: bool = True
    
    # Output configuration
    output_path: str = "sidecar.json"
    
    @classmethod
    def from_level(cls, level: AnalysisLevel) -> "ProcessorConfig":
        """
        Factory method to create config from analysis level.
        Sets appropriate layer enables based on level.
        """
        config = cls(level=level)
        
        if level == AnalysisLevel.MINIMAL:
            config.use_layer_1 = False
            config.use_layer_2 = False
            config.use_layer_3 = False
            
        elif level == AnalysisLevel.FAST:
            config.use_layer_2 = False
            config.use_layer_3 = False
            
        elif level == AnalysisLevel.STANDARD:
            config.use_layer_3 = False
            
        # DEEP enables all layers (default behavior)
        
        return config
    
    @classmethod
    def from_layers(cls, layers: list[int]) -> "ProcessorConfig":
        """
        Factory method to create config from a list of layer numbers.
        Example: from_layers([0, 1]) enables only layers 0 and 1.
        """
        config = cls(level=AnalysisLevel.STANDARD)
        
        # Disable all first
        config.use_layer_0 = False
        config.use_layer_1 = False
        config.use_layer_2 = False
        config.use_layer_3 = False
        
        # Enable specified layers
        for layer in layers:
            if layer == 0:
                config.use_layer_0 = True
            elif layer == 1:
                config.use_layer_1 = True
            elif layer == 2:
                config.use_layer_2 = True
            elif layer == 3:
                config.use_layer_3 = True
        
        return config
    
    def get_enabled_layers(self) -> list[int]:
        """Returns list of enabled layer numbers."""
        layers = []
        if self.use_layer_0:
            layers.append(0)
        if self.use_layer_1:
            layers.append(1)
        if self.use_layer_2:
            layers.append(2)
        if self.use_layer_3:
            layers.append(3)
        return layers
    
    def __str__(self) -> str:
        layers = self.get_enabled_layers()
        return f"ProcessorConfig(level={self.level.value}, layers={layers})"
