# Project Title: SEC EDGAR Data Analysis

## Description
This project is designed to analyze SEC EDGAR filings for specific keywords ("suchbegriffe") and generate a summary of results. The project processes company filings, extracts relevant data, and saves the results in an Excel file.

## Project Structure
```
requirements.txt
data/
    suchbegriffe.json
    Unternehmensliste Masterarbeit Mai 2025.xlsx
output/
    results.xlsx
src/
    main.py
    test.ipynb
```

- **requirements.txt**: Contains the Python dependencies for the project.
- **data/**: Contains input data files such as keywords (suchbegriffe.json) and a list of companies (Excel file).
- **output/**: Stores the generated results (Excel file).
- **src/**: Contains the main Python script (main.py) and a Jupyter notebook for testing (test.ipynb).

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
1. Place the input files (`suchbegriffe.json` and `Unternehmensliste Masterarbeit Mai 2025.xlsx`) in the `data/` directory. The `data` folder already exists with the required files, but you can replace them to analyze new data.
2. Run the main script:
   ```bash
   python src/main.py
   ```
3. The results will be saved in the `output/` directory as `results.xlsx`.

## Key Features
- Downloads SEC EDGAR filings for specified companies.
- Searches for predefined keywords in the filings.
- Generates a summary of keyword occurrences.
- Outputs the results in an Excel file.

## Dependencies
- Python 3.8+
- pandas
- sec-edgar-downloader
- openpyxl

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Author
Simon Albani
Paul Tillen