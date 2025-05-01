# PDF Table & Sum Analysis

A comprehensive Python tool for extracting tables from PDF documents and identifying numerical relationships, particularly vertical sums in financial statements and reports.


## 🔍 Overview

This utility tackles the challenging problem of extracting and validating tabular data from PDFs with a focus on numerical values and sum relationships. It uses multiple extraction methods to maximize accuracy and provides detailed output for analysis.

### Key Features

- **Multi-Method Table Extraction**: Uses multiple libraries (pdfplumber, camelot) to handle various table formats
- **Numeric Value Detection**: Identifies and extracts numbers from complex text
- **Sum Relationship Analysis**: Automatically detects vertical sum patterns in columns
- **Complete Reporting**: Generates detailed CSV and JSON outputs for further analysis
- **Batch Processing**: Handles single files or entire directories of PDFs

## 📊 Project Architecture

The project is centered around the `PDFTableProcessor` class with a pipeline approach:

```
PDF Document → Table Extraction → Numeric Value Identification → Sum Detection → Reports & Visualization
```

### Components Breakdown

1. **PDF Loading**: Uses PdfReader and pdfplumber to open and prepare documents
2. **Table Extraction**: 
   - pdfplumber for basic table structures
   - camelot in both "lattice" (bordered) and "stream" (borderless) modes
3. **Numeric Processing**: Regular expressions to identify and clean numeric values
4. **Sum Detection Algorithms**: Multiple pattern detection approaches:
   - First value is sum of others
   - Last value is sum of others
   - Any value could be sum of sequential subset
5. **Output Generation**: Produces CSV tables and JSON relationship reports

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Java Runtime Environment (for Tabula/Camelot)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pdf-table-analysis.git
   cd pdf-table-analysis
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies

```
pdfplumber
camelot-py
tabula-py
numpy
pandas
PyPDF2
```

## 💻 Usage

### Basic Usage

```python
from pdf_table_processor import analyze_pdf

# Process a single PDF
report = analyze_pdf("path/to/your/financial-statement.pdf")
```

### Batch Processing

```python
from pdf_table_processor import batch_process_pdfs

# Process all PDFs in a directory
batch_process_pdfs("path/to/pdf/directory")
```

### Command Line Interface

```bash
python pdf_analyzer.py Financial-Statement-11.pdf
```

## 📋 Output Files

The tool generates several output files in the specified output directory:

1. **CSV Tables**: One file per detected table with naming pattern:
   `{filename}_p{page}_t{table_number}_{method}.csv`

2. **Sum Relationships**: JSON file with all detected numerical relationships:
   `{filename}_sums.json`

3. **Combined Report**: When batch processing, a summary of all analyzed files:
   `combined_report.json`

## 🧠 How It Works

### Table Extraction Strategy

The code uses multiple extraction methods because PDFs can represent tables in different ways:

1. **pdfplumber**: Good for basic tables with clear structure
2. **camelot (lattice)**: Excels at tables with visible borders/lines
3. **camelot (stream)**: Better for tables defined by whitespace without borders

For each pattern, the code:
- Groups numeric values by column
- Tests various combinations of values
- Validates potential sums with a small tolerance (0.01) for rounding errors

## 🔧 Future Improvements

- **OCR Integration**: Currently, the tool doesn't use OCR but could be enhanced with:
  - Tesseract OCR (open-source)
  - Amazon Textract (paid AWS service)
  - Mistral OCR or other commercial OCR engines
  
- **Horizontal Sum Detection**: Add capability to detect row-based sums
- **Machine Learning Classification**: Train models to better identify table headers and sum rows
- **PDF Preprocessing**: Add image enhancement for better extraction from scanned documents
- **Interactive Visualization**: Web interface to view and validate detected relationships


