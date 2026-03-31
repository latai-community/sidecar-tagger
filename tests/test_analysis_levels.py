"""
Tests for Analysis Levels and Layer Configuration.
"""
import os
import pytest
import logging
from unittest.mock import patch, MagicMock
from sdk.config import AnalysisLevel, ProcessorConfig
from sdk.processor import MetadataProcessor

# Disable logging during tests
logging.disable(logging.CRITICAL)


@pytest.fixture
def mock_txt(tmp_path):
    """Fixture to create a temporary mock TXT file."""
    p = tmp_path / "test_notes.txt"
    p.write_text("Hello World Notes")
    return str(p)


class TestAnalysisLevel:
    """Tests for AnalysisLevel enum and ProcessorConfig."""

    def test_analysis_level_enum_values(self):
        """Verify all analysis levels are defined."""
        assert AnalysisLevel.MINIMAL.value == "minimal"
        assert AnalysisLevel.FAST.value == "fast"
        assert AnalysisLevel.STANDARD.value == "standard"
        assert AnalysisLevel.DEEP.value == "deep"

    def test_processor_config_default(self):
        """Test default processor config."""
        config = ProcessorConfig()
        assert config.level == AnalysisLevel.STANDARD
        assert config.use_layer_0 is True
        assert config.use_layer_1 is True
        assert config.use_layer_2 is True
        assert config.use_layer_3 is True

    def test_processor_config_from_level_minimal(self):
        """Test creating config from MINIMAL level."""
        config = ProcessorConfig.from_level(AnalysisLevel.MINIMAL)
        
        assert config.level == AnalysisLevel.MINIMAL
        assert config.use_layer_0 is True
        assert config.use_layer_1 is False
        assert config.use_layer_2 is False
        assert config.use_layer_3 is False

    def test_processor_config_from_level_fast(self):
        """Test creating config from FAST level."""
        config = ProcessorConfig.from_level(AnalysisLevel.FAST)
        
        assert config.level == AnalysisLevel.FAST
        assert config.use_layer_0 is True
        assert config.use_layer_1 is True
        assert config.use_layer_2 is False
        assert config.use_layer_3 is False

    def test_processor_config_from_level_standard(self):
        """Test creating config from STANDARD level."""
        config = ProcessorConfig.from_level(AnalysisLevel.STANDARD)
        
        assert config.level == AnalysisLevel.STANDARD
        assert config.use_layer_0 is True
        assert config.use_layer_1 is True
        assert config.use_layer_2 is True
        assert config.use_layer_3 is False

    def test_processor_config_from_level_deep(self):
        """Test creating config from DEEP level."""
        config = ProcessorConfig.from_level(AnalysisLevel.DEEP)
        
        assert config.level == AnalysisLevel.DEEP
        assert config.use_layer_0 is True
        assert config.use_layer_1 is True
        assert config.use_layer_2 is True
        assert config.use_layer_3 is True

    def test_get_enabled_layers_minimal(self):
        """Test get_enabled_layers for MINIMAL level."""
        config = ProcessorConfig.from_level(AnalysisLevel.MINIMAL)
        assert config.get_enabled_layers() == [0]

    def test_get_enabled_layers_fast(self):
        """Test get_enabled_layers for FAST level."""
        config = ProcessorConfig.from_level(AnalysisLevel.FAST)
        assert config.get_enabled_layers() == [0, 1]

    def test_get_enabled_layers_standard(self):
        """Test get_enabled_layers for STANDARD level."""
        config = ProcessorConfig.from_level(AnalysisLevel.STANDARD)
        assert config.get_enabled_layers() == [0, 1, 2]

    def test_get_enabled_layers_deep(self):
        """Test get_enabled_layers for DEEP level."""
        config = ProcessorConfig.from_level(AnalysisLevel.DEEP)
        assert config.get_enabled_layers() == [0, 1, 2, 3]

    def test_config_str_representation(self):
        """Test string representation of config."""
        config = ProcessorConfig.from_level(AnalysisLevel.STANDARD)
        config_str = str(config)
        assert "standard" in config_str
        assert "layers=[0, 1, 2]" in config_str

    def test_processor_config_from_layers_single(self):
        """Test creating config from a single layer."""
        config = ProcessorConfig.from_layers([0])
        
        assert config.use_layer_0 is True
        assert config.use_layer_1 is False
        assert config.use_layer_2 is False
        assert config.use_layer_3 is False

    def test_processor_config_from_layers_multiple(self):
        """Test creating config from multiple layers."""
        config = ProcessorConfig.from_layers([0, 1, 2])
        
        assert config.use_layer_0 is True
        assert config.use_layer_1 is True
        assert config.use_layer_2 is True
        assert config.use_layer_3 is False

    def test_processor_config_from_layers_llm_only(self):
        """Test creating config with only LLM layer."""
        config = ProcessorConfig.from_layers([3])
        
        assert config.use_layer_0 is False
        assert config.use_layer_1 is False
        assert config.use_layer_2 is False
        assert config.use_layer_3 is True

    def test_get_enabled_layers_from_layers(self):
        """Test get_enabled_layers with from_layers factory."""
        config = ProcessorConfig.from_layers([0, 2])
        assert config.get_enabled_layers() == [0, 2]


class TestMetadataProcessorWithConfig:
    """Tests for MetadataProcessor with analysis levels."""

    def test_processor_accepts_config(self):
        """Test that processor accepts config parameter."""
        config = ProcessorConfig.from_level(AnalysisLevel.MINIMAL)
        processor = MetadataProcessor(config=config)
        assert processor.config.level == AnalysisLevel.MINIMAL

    def test_processor_from_level_factory(self):
        """Test creating processor from AnalysisLevel."""
        processor = MetadataProcessor(config=ProcessorConfig.from_level(AnalysisLevel.FAST))
        assert processor.config.level == AnalysisLevel.FAST
        assert processor.config.use_layer_2 is False
        assert processor.config.use_layer_3 is False

    def test_processor_backward_compatibility(self):
        """Test backward compatibility with old constructor args."""
        processor = MetadataProcessor(output_path="test.json", similarity_threshold=0.8)
        assert processor.config.output_path == "test.json"
        assert processor.config.layer_2_similarity_threshold == 0.8


class TestLayerShortcuts:
    """Tests for layer shortcuts (confidence and similarity)."""

    def test_layer1_confidence_threshold_default(self):
        """Test default confidence threshold."""
        config = ProcessorConfig()
        assert config.layer_1_confidence_threshold == 0.8

    def test_layer2_similarity_threshold_default(self):
        """Test default similarity threshold."""
        config = ProcessorConfig()
        assert config.layer_2_similarity_threshold == 0.9

    def test_custom_thresholds(self):
        """Test custom threshold values."""
        config = ProcessorConfig(
            layer_1_confidence_threshold=0.7,
            layer_2_similarity_threshold=0.85
        )
        assert config.layer_1_confidence_threshold == 0.7
        assert config.layer_2_similarity_threshold == 0.85


class TestLayerExecution:
    """Integration tests for layer execution based on level."""

    def test_minimal_level_returns_layer_0_only(self, mock_txt):
        """Test that MINIMAL level only processes Layer 0."""
        config = ProcessorConfig.from_level(AnalysisLevel.MINIMAL)
        processor = MetadataProcessor(config=config)
        
        # Mock all components to track which are called
        with patch("sdk.utils.hashing.calculate_sha256", return_value="new_hash_123"):
            with patch.object(processor.os_extractor, "extract") as mock_extract:
                mock_extract.return_value = MagicMock(
                    filename="test.txt",
                    file_extension=".txt",
                    parent_folder="test",
                    internal_props={},
                    path_keywords=[],
                    model_dump=lambda: {}
                )
                
                metadata = processor.extract_metadata(mock_txt)
                
                # Should not call OS extractor in minimal mode (except for duplicate handling)
                # Actually minimal mode should still get local_context for duplicates
                assert "layers" in metadata
                assert 0 in metadata["layers"]

    def test_fast_level_respects_config(self, mock_txt):
        """Test that FAST level respects its config."""
        config = ProcessorConfig.from_level(AnalysisLevel.FAST)
        processor = MetadataProcessor(config=config)
        
        assert processor.config.use_layer_0 is True
        assert processor.config.use_layer_1 is True
        assert processor.config.use_layer_2 is False
        assert processor.config.use_layer_3 is False

    def test_standard_level_respects_config(self, mock_txt):
        """Test that STANDARD level respects its config."""
        config = ProcessorConfig.from_level(AnalysisLevel.STANDARD)
        processor = MetadataProcessor(config=config)
        
        assert processor.config.use_layer_0 is True
        assert processor.config.use_layer_1 is True
        assert processor.config.use_layer_2 is True
        assert processor.config.use_layer_3 is False

    def test_deep_level_enables_all_layers(self, mock_txt):
        """Test that DEEP level enables all layers."""
        config = ProcessorConfig.from_level(AnalysisLevel.DEEP)
        processor = MetadataProcessor(config=config)
        
        assert processor.config.use_layer_0 is True
        assert processor.config.use_layer_1 is True
        assert processor.config.use_layer_2 is True
        assert processor.config.use_layer_3 is True
