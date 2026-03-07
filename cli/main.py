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

# Add project root to sys.path for robust relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk.processor import MetadataProcessor
from sdk.exceptions import SidecarException
from sdk.reporter import FindingsReporter

# Logger configuration
logger = logging.getLogger("SidecarCLI")

def get_all_files(paths: List[str]) -> List[str]:
    """
    Recursively collects all supported files from the given list of paths.
    Pillar 7: Resource-safe file identification.
    """
    # Note: Extensions are now centrally managed by the Processor's Parser Registry
    # But we define them here for early filtering.
    supported_extensions = {
        '.pdf', '.xlsx', '.xls', '.jpg', '.jpeg', '.png', '.webp', '.bmp',
        '.txt', '.md', '.log'
    }
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
                    if os.path.splitext(file)[1].lower() in supported_extensions:
                        all_files.append(os.path.join(root, file))
            
    return all_files

def main() -> None:
    """Main execution entry point with structured error handling (Pillar 3)."""
    parser = argparse.ArgumentParser(
        description="Sidecar Tagger CLI - Generate consolidated, semantically-enriched metadata.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('inputs', nargs='+', help='Files or directories to process recursively.')
    parser.add_argument('--output-dir', '-o', default='.', help='Custom directory for sidecar.json.')
    parser.add_argument('--min-confidence', '-m', type=float, default=0.0, help='Filter metadata by confidence score.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable detailed process logging.')
    parser.add_argument('--overwrite', action='store_true', help='Replace existing sidecar.json if present.')

    args = parser.parse_args()

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
        
        processor = MetadataProcessor(output_path=output_path)
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

if __name__ == "__main__":
    main()
