import os
import time

from company_extractor import CompanyExtractor
from report_analyzer import ReportAnalyzer
from logger_config import setup_logger

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, ".."))
data_dir = os.path.join(project_dir, "data")
output_dir = os.path.join(project_dir, "output")
reports_dir = os.path.join(project_dir, "sec-reports/")


if __name__ == "__main__": 
    start_time = time.time()
    
    # Setup logging
    logger = setup_logger(output_dir)
    logger.info("Starting SEC EDGAR Data Analysis")
    
    extractor = CompanyExtractor(data_dir)
    companies = extractor.extract()

    analyzer = ReportAnalyzer(data_dir, reports_dir, output_dir)
    results = analyzer.analyze(companies)
    analyzer.save_results_to_excel()
    analyzer.save_results_to_csv()

    # shutil.rmtree(reports_dir)

    elapsed_time = time.time() - start_time
    logger.info(f"Analysis completed successfully in {elapsed_time:.2f} seconds")
    logger.info("Results saved to Excel and CSV files")