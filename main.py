import os
import re
import json
import numpy as np
import pandas as pd
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')
import pdfplumber
import tabula
from PyPDF2 import PdfReader
import camelot

class PDFTableProcessor:
    def __init__(self, pdf_path):
        """Initialize with path to PDF file"""
        self.pdf_path = pdf_path
        self.tables = [] 
        self.numeric_data = []  
        self.sum_relationships = []  
        
        print(f"Processing PDF: {os.path.basename(pdf_path)}")
        self._load_pdf()
    
    def _load_pdf(self):
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PdfReader(file)
                self.num_pages = len(reader.pages)
                print(f"Detected {self.num_pages} pages in document")
                
            self.pdf = pdfplumber.open(self.pdf_path)
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
            raise
    
    def extract_tables(self):
        print("Extracting tables...")
        
        extracted_tables = []
        
        # Method 1: pdfplumber
        try:
            for page_num, page in enumerate(self.pdf.pages):
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        cleaned_table = []
                        for row in table:
                            cleaned_row = []
                            for cell in row:
                                # Clean up cid encoding issues
                                if cell is not None:
                                    # Replace CID pattern with empty string
                                    cell_str = str(cell)
                                    clean_cell = re.sub(r'\(cid:\d+\)', '', cell_str).strip()
                                    cleaned_row.append(clean_cell)
                                else:
                                    cleaned_row.append('')
                            cleaned_table.append(cleaned_row)
                        
                        extracted_tables.append({
                            'page': page_num + 1,
                            'method': 'pdfplumber',
                            'data': cleaned_table
                        })
        except Exception as e:
            print(f"pdfplumber extraction error: {e}")
        
        # Method 2: camelot (good for bordered and borderless tables)
        try:
            # Try lattice mode first (for tables with borders)
            camelot_tables = camelot.read_pdf(self.pdf_path, pages='all', flavor='lattice')
            for i, table in enumerate(camelot_tables):
                # Clean the table data
                cleaned_data = []
                for row in table.data:
                    cleaned_row = []
                    for cell in row:
                        # Replace CID pattern
                        clean_cell = re.sub(r'\(cid:\d+\)', '', cell).strip()
                        cleaned_row.append(clean_cell)
                    cleaned_data.append(cleaned_row)
                
                extracted_tables.append({
                    'page': table.page,
                    'method': 'camelot_lattice',
                    'data': cleaned_data
                })
                
            # Then try stream mode (for tables without borders)
            camelot_tables = camelot.read_pdf(self.pdf_path, pages='all', flavor='stream')
            for i, table in enumerate(camelot_tables):
                # Clean the table data
                cleaned_data = []
                for row in table.data:
                    cleaned_row = []
                    for cell in row:
                        # Replace CID pattern
                        clean_cell = re.sub(r'\(cid:\d+\)', '', cell).strip()
                        cleaned_row.append(clean_cell)
                    cleaned_data.append(cleaned_row)
                
                extracted_tables.append({
                    'page': table.page,
                    'method': 'camelot_stream',
                    'data': cleaned_data
                })
        except Exception as e:
            print(f"camelot extraction error: {e}")
        
        # Store the extracted tables
        self.tables = extracted_tables
        print(f"Extracted {len(extracted_tables)} potential tables")
        
        return extracted_tables
    
    def identify_numeric_values(self):
        """Identify and extract numeric values from the tables"""
        print("Identifying numeric values...")
        numeric_data = []
        
        for table_info in self.tables:
            table = table_info['data']
            page = table_info['page']
            
            table_numeric_data = []
            
            for row_idx, row in enumerate(table):
                for col_idx, cell in enumerate(row):
                    # Skip empty cells
                    if cell is None or (isinstance(cell, str) and cell.strip() == ''):
                        continue
                    
                    # Convert cell to string if it's not already
                    cell_str = str(cell).strip()
                    
                    numeric_match = re.search(r'[-+$£€]?\s*[\d,]+\.?\d*', cell_str)
                    if numeric_match:
                        numeric_str = numeric_match.group(0)
                        # Clean the numeric string (remove commas and currency symbols)
                        numeric_str = numeric_str.replace(',', '').replace('$', '').replace('£', '').replace('€', '')
                        
                        try:
                            numeric_value = float(numeric_str)
                            # Store the numeric value with its location info
                            table_numeric_data.append({
                                'value': numeric_value,
                                'original_text': cell_str,
                                'row': row_idx,
                                'col': col_idx
                            })
                        except ValueError:
                            pass
            
            if table_numeric_data:
                numeric_data.append({
                    'page': page,
                    'method': table_info['method'],
                    'numeric_values': table_numeric_data
                })
        
        self.numeric_data = numeric_data
        total_numbers = sum(len(table['numeric_values']) for table in numeric_data)
        print(f"Identified {total_numbers} numeric values across {len(numeric_data)} tables")
        
        return numeric_data
    
    def detect_vertical_sum_relationships(self):
        print("Detecting vertical sum relationships...")
        sum_relationships = []
        
        for table_data in self.numeric_data:
            table_numbers = table_data['numeric_values']
            
            # Skip if table has too few numbers for sums
            if len(table_numbers) < 3:
                continue
            
            # Group numbers by column
            cols = defaultdict(list)
            for num_info in table_numbers:
                cols[num_info['col']].append(num_info)
            
            # Check for vertical sums (down columns)
            for col_idx, col_nums in cols.items():
                if len(col_nums) < 3:  # Need at least 3 numbers for a sum relationship
                    continue
                
                # Sort by row for proper order
                col_nums = sorted(col_nums, key=lambda x: x['row'])
                
                if len(col_nums) >= 3:
                    components = col_nums[:-1]
                    potential_sum = col_nums[-1]
                    component_sum = sum(c['value'] for c in components)
                    
                    if abs(component_sum - potential_sum['value']) < 0.01:
                        sum_relationships.append({
                            'page': table_data['page'],
                            'type': 'vertical',
                            'col': col_idx,
                            'sum_value': potential_sum['value'],
                            'sum_position': {'row': potential_sum['row'], 'col': potential_sum['col']},
                            'components': [{'value': c['value'], 
                                          'position': {'row': c['row'], 'col': c['col']}}
                                         for c in components],
                            'valid': True,
                            'computed_sum': component_sum,
                            'pattern': 'last_is_sum'
                        })
                
                if len(col_nums) >= 3:
                    potential_sum = col_nums[0]
                    components = col_nums[1:]
                    component_sum = sum(c['value'] for c in components)
                    
                    if abs(component_sum - potential_sum['value']) < 0.01:
                        sum_relationships.append({
                            'page': table_data['page'],
                            'type': 'vertical',
                            'col': col_idx,
                            'sum_value': potential_sum['value'],
                            'sum_position': {'row': potential_sum['row'], 'col': potential_sum['col']},
                            'components': [{'value': c['value'], 
                                          'position': {'row': c['row'], 'col': c['col']}}
                                         for c in components],
                            'valid': True,
                            'computed_sum': component_sum,
                            'pattern': 'first_is_sum'
                        })
                
                if len(col_nums) >= 4:  # Need at least 4 numbers for this pattern
                    for i in range(len(col_nums)):
                        potential_sum = col_nums[i]
                        
                        # Try different window sizes for components
                        for window_size in range(2, min(len(col_nums), 5)):  # Try reasonable window sizes
                            for start in range(len(col_nums) - window_size):
                                # Skip if potential sum is in the component range
                                if start <= i < start + window_size:
                                    continue
                                
                                components = col_nums[start:start+window_size]
                                component_sum = sum(c['value'] for c in components)
                                
                                if abs(component_sum - potential_sum['value']) < 0.01:
                                    sum_relationships.append({
                                        'page': table_data['page'],
                                        'type': 'vertical',
                                        'col': col_idx,
                                        'sum_value': potential_sum['value'],
                                        'sum_position': {'row': potential_sum['row'], 'col': potential_sum['col']},
                                        'components': [{'value': c['value'], 
                                                      'position': {'row': c['row'], 'col': c['col']}}
                                                     for c in components],
                                        'valid': True,
                                        'computed_sum': component_sum,
                                        'pattern': 'subset_sum'
                                    })
        
        self.sum_relationships = sum_relationships
        print(f"Detected {len(sum_relationships)} vertical sum relationships")
        
        return sum_relationships
    
    def create_report(self):
        print("Generating report...")
        
        report = {
            "filename": os.path.basename(self.pdf_path),
            "num_pages": self.num_pages,
            "tables_extracted": len(self.tables),
            "numeric_values_found": sum(len(table['numeric_values']) for table in self.numeric_data),
            "sum_relationships": []
        }
        
        # Format sum relationships for the report
        for relation in self.sum_relationships:
            report["sum_relationships"].append({
                "page": relation["page"],
                "type": relation["type"],
                "column": relation["col"],
                "sum_value": relation["sum_value"],
                "component_values": [comp["value"] for comp in relation["components"]],
                "valid": relation["valid"],
                "computed_sum": relation["computed_sum"],
                "pattern": relation.get("pattern", "unknown")
            })
        
        return report
    
    def visualize_results(self, output_dir="output"):
        """Create visual representations of the extracted tables and sums"""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        base_filename = os.path.splitext(os.path.basename(self.pdf_path))[0]
        
        # Generate tables as CSV files
        for i, table_info in enumerate(self.tables):
            table = table_info['data']
            method = table_info['method']
            page = table_info['page']
            
            max_cols = max(len(row) for row in table) if table else 0
            normalized_table = [row + [''] * (max_cols - len(row)) for row in table] if max_cols > 0 else []
            
            df = pd.DataFrame(normalized_table)
            csv_path = os.path.join(output_dir, f"{base_filename}_p{page}_t{i+1}_{method}.csv")
            df.to_csv(csv_path, index=False, header=False)
        
        # Save sum relationships as JSON
        json_path = os.path.join(output_dir, f"{base_filename}_sums.json")
        with open(json_path, 'w') as f:
            json.dump(self.sum_relationships, f, indent=2)
        
        print(f"Results saved to {output_dir} directory")
    
    def process_all(self, output_dir="output"):
        """Run the complete processing pipeline"""
        self.extract_tables()
        self.identify_numeric_values()
        self.detect_vertical_sum_relationships()
        report = self.create_report()
        self.visualize_results(output_dir)
        return report

def analyze_pdf(pdf_path, output_dir="output"):
    """
    Main function to analyze a PDF for tables and vertical sum relationships
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save output files
    
    Returns:
        Report dictionary with analysis results
    """
    print(f"\n{'='*50}")
    print(f"Processing: {os.path.basename(pdf_path)}")
    print(f"{'='*50}\n")
    
    # Create processor
    processor = PDFTableProcessor(pdf_path)
    
    # Run complete analysis
    report = processor.process_all(output_dir)
    
    # Print summary
    print("\nAnalysis Summary:")
    print(f"- Extracted {report['tables_extracted']} tables")
    print(f"- Found {report['numeric_values_found']} numeric values")
    print(f"- Detected {len(report['sum_relationships'])} vertical sum relationships")
    
    valid_sums = sum(1 for rel in report['sum_relationships'] if rel['valid'])
    print(f"- {valid_sums} valid sums / {len(report['sum_relationships'])} total detected")
    
    print(f"\nDetailed results saved to {output_dir} directory\n")
    
    return report

def batch_process_pdfs(pdf_dir, output_dir="output"):
    """Process all PDFs in a directory"""
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    results = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        try:
            report = analyze_pdf(pdf_path, output_dir)
            results.append(report)
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
    
    # Save combined results
    combined_report = {
        "processed_files": len(results),
        "total_tables": sum(r['tables_extracted'] for r in results),
        "total_numeric_values": sum(r['numeric_values_found'] for r in results),
        "total_sum_relationships": sum(len(r['sum_relationships']) for r in results),
        "per_file_results": results
    }
    
    report_path = os.path.join(output_dir, "combined_report.json")
    with open(report_path, 'w') as f:
        json.dump(combined_report, f, indent=2)
    
    print(f"\nBatch processing complete! Combined report saved to {report_path}")
    return combined_report


input_path = "input\Financial-Statement-11.pdf"  
output_dir = "output"   

os.makedirs(output_dir, exist_ok=True)

if os.path.isdir(input_path):
    batch_process_pdfs(input_path, output_dir)
elif os.path.isfile(input_path) and input_path.lower().endswith('.pdf'):
    analyze_pdf(input_path, output_dir)
else:
    print("Input must be a PDF file or directory containing PDF files")