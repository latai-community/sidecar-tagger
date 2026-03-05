import argparse
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk.processor import MetadataProcessor

def main():
    parser = argparse.ArgumentParser(description="Sidecar Tagger CLI - Generate consolidated metadata.")
    
    # Accept 1 to N files
    parser.add_argument('files', nargs='+', help='Files to process.')
    
    # Standard flags from skill
    parser.add_argument('--output-dir', '-o', default='.', help='Custom output directory for sidecar.json.')
    parser.add_argument('--min-confidence', '-m', type=float, default=0.0, help='Filter metadata by confidence.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging.')
    parser.add_argument('--overwrite', action='store_true', help='Replace existing sidecar.json.')

    args = parser.parse_args()

    # Construct output path for consolidated file
    output_path = os.path.join(args.output_dir, "sidecar.json")

    # If sidecar.json exists and no overwrite flag, warn user or skip
    if os.path.exists(output_path) and not args.overwrite:
        print(f"Error: {output_path} already exists. Use --overwrite to replace it.")
        sys.exit(1)

    if args.verbose:
        print(f"Processing {len(args.files)} files...")

    processor = MetadataProcessor(output_path=output_path)
    processor.process_files(args.files)

    if args.verbose:
        print("Done.")

if __name__ == "__main__":
    main()
