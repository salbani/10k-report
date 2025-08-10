import os
import logging
from company import Company
from report_analyzer import ReportAnalyzer
from logger_config import setup_logger

cik = "0000002488" 
accession_number = "0001193125-13-069422"

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, ".."))
data_dir = os.path.join(project_dir, "data")
output_dir = os.path.join(project_dir, "output")
reports_dir = os.path.join(project_dir, "sec-reports/")

# Setup logging
logger = setup_logger(output_dir, log_level=logging.DEBUG)

report_analyzer = ReportAnalyzer(data_dir, reports_dir, output_dir)

company = Company("Test Company", cik)
company.download_reports(reports_dir, "2013-01-01")

if company.company_reports_dir is not None:
    result = report_analyzer.analyze_report(
        os.path.join(company.company_reports_dir, accession_number, "full-submission.txt"),
        True,
    )
else:
    raise ValueError("Company reports directory is not set")

logger.info(f"Test result: {result}")
