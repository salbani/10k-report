import os
import logging
from company import Company
from report_analyzer import ReportAnalyzer
from logger_config import setup_logger

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, ".."))
data_dir = os.path.join(project_dir, "data")
output_dir = os.path.join(project_dir, "output")
reports_dir = os.path.join(project_dir, "sec-reports/")

# Setup logging
logger = setup_logger(output_dir, log_level=logging.DEBUG)

report_analyzer = ReportAnalyzer(data_dir, reports_dir, output_dir)

company = Company("Test Company", "0000769397")
company.download_reports(reports_dir, "2013-01-01")

result = report_analyzer.analyze_report(
    "/Users/simon/Workspace/10k-report/sec-reports/sec-edgar-filings/0000769397/10-K/0000769397-22-000019/full-submission.txt",
    True,
)

logger.info(f"Test result: {result}")
