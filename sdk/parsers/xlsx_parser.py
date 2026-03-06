import openpyxl
import os

def extract_xlsx_content(file_path: str) -> str:
    """
    Extracts data from an XLSX file using openpyxl.
    Iterates through all sheets and summarizes rows and columns.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    summary_parts = []
    try:
        workbook = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
        sheet_names = workbook.sheetnames
        total_sheets = len(sheet_names)
        
        summary_parts.append(f"Workbook contains {total_sheets} sheets: {', '.join(sheet_names)}")
        
        # Sampling strategy: First 2, Middle 1, Last 2 sheets
        sheets_to_read = set()
        
        # Start
        for i in range(min(2, total_sheets)):
            sheets_to_read.add(sheet_names[i])
            
        # Middle
        mid = total_sheets // 2
        sheets_to_read.add(sheet_names[mid])
        
        # End
        for i in range(max(0, total_sheets - 2), total_sheets):
            sheets_to_read.add(sheet_names[i])
            
        # Process unique sampled sheets
        for sheet_name in sorted(list(sheets_to_read), key=lambda x: sheet_names.index(x)):
            sheet = workbook[sheet_name]
            # Basic summary per sheet
            rows = sheet.max_row if sheet.max_row else 0
            cols = sheet.max_column if sheet.max_column else 0
            summary_parts.append(f"Sheet '{sheet_name}': {rows} rows, {cols} columns.")
            
            # Extract first few rows for context (limited to avoid massive output)
            sample_data = []
            for row in sheet.iter_rows(max_row=5, values_only=True):
                # Filter out None values and convert to string
                row_str = " | ".join([str(cell) for cell in row if cell is not None])
                if row_str.strip():
                    sample_data.append(row_str)
            
            if sample_data:
                summary_parts.append("Sample rows:")
                summary_parts.extend(sample_data)
        
        return "\n".join(summary_parts)
    except Exception as e:
        return f"Error parsing XLSX: {str(e)}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(extract_xlsx_content(sys.argv[1]))
    else:
        print("Usage: python xlsx_parser.py <path_to_xlsx>")
