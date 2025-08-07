# Project Title: SEC EDGAR Data Analysis

## Description
This project analyzes SEC EDGAR 10-K filings for specific technology-related keywords and generates comprehensive results. The system downloads company filings, extracts the "Item 1: Description of Business" section, searches for predefined keywords, and saves detailed analysis results in both Excel and CSV formats.

## Project Structure
```
requirements.txt
data/
    keywords.json
    Unternehmensliste Masterarbeit Mai 2025.xlsx
output/
    sec_report_analysis_results.xlsx
    sec_report_analysis_results.csv
    analysis_errors.txt
sec-reports/
    sec-edgar-filings/
        [company CIK folders with downloaded 10-K filings]
src/
    main.py
    company.py
    company_extractor.py
    report_analyzer.py
    test_report.py
    test.ipynb
```

- **requirements.txt**: Contains the Python dependencies for the project.
- **output/**: Stores analysis results including Excel/CSV files and error logs.
- **sec-reports/**: Contains downloaded SEC EDGAR filings organized by company CIK.
- **src/**: Contains the main application code with modular components.
  - `main.py`: Main application entry point
  - `company.py`: Company class with rate-limited SEC filing download functionality
  - `company_extractor.py`: Extracts company information from Excel file
  - `report_analyzer.py`: Analyzes 10-K filings for keyword occurrences
  - `test_report.py`: Testing utilities
  - `test.ipynb`: Jupyter notebook for development and testing

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place the input files (`keywords.json` and `Unternehmensliste Masterarbeit Mai 2025.xlsx`) in the `data/` directory. The `data` folder already exists with the required files, but you can replace them to analyze new data.

2. Run the main script:

   ```bash
   python src/main.py
   ```

3. The results will be saved in the `output/` directory:
   - `sec_report_analysis_results.xlsx`: Complete analysis results in Excel format
   - `sec_report_analysis_results.csv`: Same results in CSV format
   - `analysis_errors.txt`: Log of any processing errors

## Key Features

- **Automated SEC Filing Download**: Downloads 10-K filings from SEC EDGAR database with rate limiting
- **Targeted Text Analysis**: Extracts and analyzes "Item 1: Description of Business" sections
- **Technology Keyword Detection**: Searches for 80+ predefined technology-related keywords
- **Multi-format Output**: Generates results in both Excel and CSV formats
- **Error Handling**: Comprehensive error logging and graceful failure handling
- **Parallel Processing**: Utilizes multiprocessing for efficient company analysis
- **Process-safe Rate Limiting**: Prevents overwhelming SEC servers with file-based locking

## Keywords Analyzed

The system searches for technology-related terms including:

- AI and Machine Learning: "artificial intelligence", "AI", "algorithm", "machine learning"
- Digital Technologies: "digital", "digitalization", "cloud computing", "blockchain"
- Internet and Web: "internet", "online", "website", "e-commerce"
- Mobile and IoT: "smartphone", "mobile", "internet of things", "IoT"
- And many more (80+ keywords total)

## Dependencies

- Python 3.8+
- pandas
- sec-edgar-downloader
- openpyxl
- beautifulsoup4
- requests
- lxml

## Output Format

The analysis results include:

- Company Name and CIK
- Report Year and Accession Number
- Individual keyword frequency counts
- Total word count for analyzed sections

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Authors

Simon Albani  \
Paul Tillen