import argparse
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk.processor import MetadataProcessor

def get_all_files(paths):
    """Recursively collects all supported files from the given list of paths."""
    supported_extensions = {'.pdf', '.xlsx', '.xls', '.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    all_files = []
    
    for path in paths:
        if os.path.isfile(path):
            all_files.append(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if os.path.splitext(file)[1].lower() in supported_extensions:
                        all_files.append(os.path.join(root, file))
        else:
            print(f"Warning: {path} is not a valid file or directory. Skipping.")
            
    return all_files

def main():
    parser = argparse.ArgumentParser(description="Sidecar Tagger CLI - Generate consolidated metadata.")
    
    # Accept 1 to N files or directories
    parser.add_argument('inputs', nargs='+', help='Files or directories to process.')
    
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

    # Collect all files from inputs (files or folders)
    files_to_process = get_all_files(args.inputs)

    if not files_to_process:
        print("No supported files found to process.")
        sys.exit(0)

    if args.verbose:
        print(f"Found {len(files_to_process)} supported files. Starting processing...")

    processor = MetadataProcessor(output_path=output_path)
    processor.process_files(files_to_process)

    if args.verbose:
        print(f"Done. Metadata saved to {output_path}")

if __name__ == "__main__":
    main()
