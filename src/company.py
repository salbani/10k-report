import os
import shutil
import time
import fcntl
import tempfile
import logging
from typing import Any

from sec_edgar_downloader import Downloader  # type: ignore
from logger_config import get_logger

report_folder_name = "10-K"
company_name = "sec-edgar-filings"

class Company:
    # Process-safe rate limiting using file locking
    _min_delay_between_downloads = 2.0  # Minimum seconds between downloads
    _lock_file_path = os.path.join(tempfile.gettempdir(), "sec_download_lock.txt")
    
    def __init__(self, name: str, cik: str):
        self.company_reports_dir: str | None = None
        self.name = name
        self.cik = cik
        self.report_paths: list[str] = []
        self.logger = get_logger("sec_analyzer.company")

    def download_reports(self, reports_dir: str, after_date: str):
        self.company_reports_dir = company_reports_dir = os.path.join(reports_dir, company_name, self.cik, report_folder_name)

        self._rate_limit()
        dl = Downloader(company_name, "jaspeb97@zedat.fu-berlin.de", reports_dir)
        dl.get(report_folder_name, self.cik, after=after_date)

        if not os.path.exists(company_reports_dir):
            self.logger.warning(f"Directory not found: {company_reports_dir}")
            return

        for folder in os.listdir(company_reports_dir):
            report_path = os.path.join(
                company_reports_dir, folder, "full-submission.txt"
            )
            if not os.path.exists(report_path):
                self.logger.warning(f"File not found: {report_path}")
                continue

            self.report_paths.append(report_path)

    def delete_reports(self):
        """Delete all downloaded reports for this company."""
        if self.company_reports_dir and os.path.exists(self.company_reports_dir):
            try:
                shutil.rmtree(self.company_reports_dir)
                self.logger.info(f"Deleted reports for {self.name} ({self.cik})")
            except Exception as e:
                self.logger.error(f"Error deleting reports for {self.name} ({self.cik}): {e}")

    def _rate_limit(self):
        """Process-safe rate limiting using file locking."""
        try:
            # Create lock file if it doesn't exist
            if not os.path.exists(Company._lock_file_path):
                with open(Company._lock_file_path, 'w') as f:
                    f.write(str(time.time()))
            
            # Use file locking for process-safe synchronization
            with open(Company._lock_file_path, 'r+') as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                
                try:
                    # Read last download time
                    lock_file.seek(0)
                    content = lock_file.read().strip()
                    last_download_time = float(content) if content else 0
                    
                    current_time = time.time()
                    time_since_last = current_time - last_download_time
                    
                    if time_since_last < Company._min_delay_between_downloads:
                        sleep_time = Company._min_delay_between_downloads - time_since_last
                        self.logger.info(f"Rate limiting: waiting {sleep_time:.2f} seconds before downloading for {self.name}")
                        time.sleep(sleep_time)
                    
                    # Update last download time
                    current_time = time.time()
                    lock_file.seek(0)
                    lock_file.write(str(current_time))
                    lock_file.truncate()
                    
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    
        except Exception as e:
            self.logger.warning(f"Rate limiting failed for {self.name}: {e}")
            # Continue without rate limiting if there's an issue


    def __repr__(self):
        return f"Company(name={self.name}, cik={self.cik}, filings={len(self.report_paths)})"
    