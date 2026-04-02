"""
Title: Sidecar Tagger CLI
Abstract: User interface for recursive file indexing and metadata generation.
Dependencies: argparse, sys, os, logging, sdk.processor, sdk.exceptions
LLM-Hints: This is the primary entry point for users. It handles recursive directory scanning.
"""

import argparse
import sys
import os
import logging
from typing import List
from pathlib import Path

from sidecar_tagger.sdk.processor import MetadataProcessor
from sidecar_tagger.sdk.config import AnalysisLevel, ProcessorConfig
from sidecar_tagger.sdk.exceptions import SidecarException
from sidecar_tagger.sdk.reporter import FindingsReporter
from sidecar_tagger.sdk.cleaner import SidecarCleaner

# Logger configuration
logger = logging.getLogger("SidecarCLI")

SUPPORTED_EXTENSIONS = {
    '.pdf', '.xlsx', '.xls', '.jpg', '.jpeg', '.png', '.webp', '.bmp',
    '.txt', '.md', '.log'
}

def get_all_files(paths: List[str]) -> List[str]:
    """
    Recursively collects all supported files from the given list of paths.
    Pillar 7: Resource-safe file identification.
    """
    all_files = []
    
    for path in paths:
        if not os.path.exists(path):
            logger.warning(f"Path not found: {path}. Skipping.")
            continue

        if os.path.isfile(path):
            all_files.append(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if os.path.splitext(file)[1].lower() in SUPPORTED_EXTENSIONS:
                        all_files.append(os.path.join(root, file))
        
    return all_files

def create_parser() -> argparse.ArgumentParser:
    """Creates the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Sidecar Tagger CLI - Generate consolidated, semantically-enriched metadata.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Process subcommand
    process_parser = subparsers.add_parser(
        "process",
        help="Generate metadata sidecars for files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    process_parser.add_argument('inputs', nargs='+', help='Files or directories to process recursively.')
    process_parser.add_argument('--output-dir', '-o', default='.', help='Custom directory for sidecar.json.')
    process_parser.add_argument('--min-confidence', '-m', type=float, default=0.0, help='Filter metadata by confidence score.')
    process_parser.add_argument('--verbose', '-v', action='store_true', help='Enable detailed process logging.')
    process_parser.add_argument('--overwrite', action='store_true', help='Replace existing sidecar.json if present.')
    process_parser.add_argument(
        '--level', '-l',
        choices=['minimal', 'fast', 'standard', 'deep'],
        default='standard',
        help='Analysis depth level: minimal (hash only), fast (OS metadata), standard (with cache), deep (full AI)'
    )
    process_parser.add_argument(
        '--layers',
        help='Comma-separated list of layers to enable (0=Hash, 1=OS, 2=Embeddings, 3=LLM). Overrides --level if specified. Example: 0,1 or 0,1,2'
    )
    process_parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.8,
        help='Confidence threshold for Layer 1 shortcut (0.0-1.0). Default: 0.8'
    )
    process_parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.9,
        help='Similarity threshold for Layer 2 cache (0.0-1.0). Default: 0.9'
    )

    # Clean subcommand
    clean_parser = subparsers.add_parser(
        "clean",
        help="Remove generated sidecar files (sidecar.json, findings.md).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    clean_parser.add_argument('--path', '-p', default='.', help='Root directory to clean.')
    clean_parser.add_argument('--dry-run', '-n', action='store_true', help='Show files that would be deleted without removing them.')

    return parser

def run_process(args) -> None:
    """Execute the process subcommand."""
    # Configure logging level based on verbosity (Pillar 4)
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(log_level)

    output_path = os.path.join(args.output_dir, "sidecar.json")

    # Guard clause: Prevent accidental data loss (Pillar 1/Java Style)
    if os.path.exists(output_path) and not args.overwrite:
        logger.error(f"Output file already exists: {output_path}. Use --overwrite to replace.")
        sys.exit(1)

    try:
        files_to_process = get_all_files(args.inputs)
        if not files_to_process:
            logger.info("No supported files found to process.")
            sys.exit(0)

        logger.info(f"Indexing {len(files_to_process)} files into {output_path}...")
        
        # Create processor config: --layers overrides --level if specified
        if args.layers:
            # Parse comma-separated layer list
            layer_list = [int(x.strip()) for x in args.layers.split(',')]
            config = ProcessorConfig.from_layers(layer_list)
            logger.info(f"Using granular layers: {layer_list}")
        else:
            config = ProcessorConfig.from_level(AnalysisLevel(args.level))
            logger.info(f"Using analysis level: {args.level}")
        
        # Apply custom thresholds if specified
        config.layer_1_confidence_threshold = args.confidence_threshold
        config.layer_2_similarity_threshold = args.similarity_threshold
        
        logger.info(f"Layers enabled: {config.get_enabled_layers()}")
        logger.info(f"Confidence threshold: {config.layer_1_confidence_threshold}")
        logger.info(f"Similarity threshold: {config.layer_2_similarity_threshold}")
        
        processor = MetadataProcessor(config=config, output_path=output_path)
        processor.process_files(files_to_process)

        logger.info(f"Done. Manifest successfully generated at {output_path}")

        # Post-Processing: Generate Findings Report
        reporter = FindingsReporter(manifest_path=output_path)
        reporter.generate_report(output_path=os.path.join(args.output_dir, "findings.md"))
        logger.info(f"Findings report generated at {os.path.join(args.output_dir, 'findings.md')}")

    except SidecarException as e:
        logger.critical(f"System execution failed: {e}")
        sys.exit(2)
    except Exception as e:
        logger.critical(f"An unexpected fatal error occurred: {e}", exc_info=args.verbose)
        sys.exit(3)

def run_clean(args) -> None:
    """Execute the clean subcommand."""
    cleaner = SidecarCleaner()
    root = Path(args.path)

    if not root.exists():
        logger.error(f"Path not found: {root}")
        sys.exit(1)

    if args.dry_run:
        files = cleaner.dry_run(root)
        mode_label = "[DRY RUN] "
        print(f"\n{mode_label}Found {len(files)} file(s) to clean:")
        for fp in files:
            print(f"  - {fp}")
        print(f"\n{mode_label}Summary: {len(files)} file(s) would be deleted.")
    else:
        result = cleaner.clean(root)
        mode_label = ""
        print(f"\nClean complete:")
        print(f"  Files found:   {result.files_found}")
        print(f"  Files deleted: {result.files_deleted}")
        if result.errors:
            print(f"  Errors:        {len(result.errors)}")
            for fp, err in result.errors:
                print(f"    - {fp}: {err}")
        if not result.errors and result.files_deleted == result.files_found:
            print("\nAll target files removed successfully.")

def main() -> None:
    """Main execution entry point with structured error handling (Pillar 3)."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "process":
        run_process(args)
    elif args.command == "clean":
        run_clean(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
