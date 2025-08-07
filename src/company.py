import os
import time
import fcntl
import tempfile
from typing import Any

from sec_edgar_downloader import Downloader  # type: ignore


class Company:
    # Process-safe rate limiting using file locking
    _min_delay_between_downloads = 2.0  # Minimum seconds between downloads
    _lock_file_path = os.path.join(tempfile.gettempdir(), "sec_download_lock.txt")
    
    def __init__(self, name: str, cik: str):
        self.name = name
        self.cik = cik
        self.report_paths: list[str] = []

    def download_reports(self, reports_dir: str, after_date: str):
        report_folder_name = "10-K"
        company_name = "sec-edgar-filings"
        company_reports_dir = os.path.join(reports_dir, company_name, self.cik, report_folder_name)

        if not os.path.exists(company_reports_dir):
            # Apply process-safe rate limiting to prevent overwhelming the SEC servers
            self._rate_limit()
            dl = Downloader(company_name, "jaspeb97@zedat.fu-berlin.de", reports_dir)
            dl.get(report_folder_name, self.cik, after=after_date)

        if not os.path.exists(company_reports_dir):
            print(f"Directory not found: {company_reports_dir}")
            return

        for folder in os.listdir(company_reports_dir):
            report_path = os.path.join(
                company_reports_dir, folder, "full-submission.txt"
            )
            if not os.path.exists(report_path):
                print(f"File not found: {report_path}")
                continue

            self.report_paths.append(report_path)

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
                        print(f"Rate limiting: waiting {sleep_time:.2f} seconds before downloading for {self.name}")
                        time.sleep(sleep_time)
                    
                    # Update last download time
                    current_time = time.time()
                    lock_file.seek(0)
                    lock_file.write(str(current_time))
                    lock_file.truncate()
                    
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    
        except Exception as e:
            print(f"Warning: Rate limiting failed for {self.name}: {e}")
            # Continue without rate limiting if there's an issue


    def __repr__(self):
        return f"Company(name={self.name}, cik={self.cik}, filings={len(self.report_paths)})"
    