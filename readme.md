# Financial Statement OCR & Verification System

A powerful system that extracts data from financial statement images using OCR, converts the data into structured JSON, and verifies the mathematical accuracy of financial calculations.

## Overview

This project combines advanced OCR (Optical Character Recognition) capabilities from Mistral AI with financial calculation verification through OpenAI's models. The system:

1. Processes financial statement images through OCR
2. Converts extracted text into structured JSON data
3. Verifies the mathematical accuracy of financial calculations
4. Outputs comprehensive analysis results

## Architecture

The system consists of two main components:

- **OCR Processing** (`main.py`): Handles image processing using Mistral's OCR and text-to-JSON conversion with Pixtral
- **Financial Verification** (`helper.py`): Validates the mathematical accuracy of all financial calculations

## Requirements

- Python 3.8+
- Mistral AI API account
- OpenAI API key (or compatible API endpoint)
- Required Python packages:
  - mistralai
  - openai
  - python-dotenv

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/financial-statement-ocr.git
cd financial-statement-ocr
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API keys:

```
MISTRAL_API_KEY=your_mistral_api_key
ENDPOINT=your_openai_compatible_endpoint
GITHUB_ACCESS_CODE=your_openai_api_key
```

## Project Structure

```
financial-statement-ocr/
├── main.py               # OCR processing logic
├── helper.py             # Financial verification logic
├── .env                  # Environment variables (API keys)
├── input/                # Input financial statement images
│   └── Financial-Statement-9_page_1.jpg
├── output/               # Generated JSON outputs
│   ├── Financial-Statement-9_page_1_ocr.json
│   └── Financial-Statement-9_page_1_result.json
└── README.md             # This file
```

## Usage

1. Place financial statement images in the `input/` directory
2. Run the main script:

```bash
python main.py
```

3. Check the `output/` directory for results:
   - `*_ocr.json`: Structured data extracted from the image
   - `*_result.json`: Verification of calculations with accuracy reports

## Workflow

1. **Image Loading**: The system loads a financial statement image and converts it to base64
2. **OCR Processing**: Mistral's OCR model extracts text from the image
3. **Text to JSON**: Pixtral model converts the OCR text into structured JSON
4. **Financial Verification**: The helper module analyzes the JSON data to verify calculations
5. **Result Output**: Final analysis is saved as JSON files in the output directory

## Customization

To process different image files, modify the file path in `main.py`:

```python
ocr_processor("input/your_financial_statement.jpg")
```

## Error Handling

The system includes basic error handling for:
- Missing input files
- API connection issues
- JSON parsing errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
