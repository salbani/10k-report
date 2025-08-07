from concurrent.futures import ThreadPoolExecutor
import html
import json
import os
import re
import logging
import pandas as pd

from company import Company
from logger_config import get_logger


class ReportAnalyzer:
    def __init__(self, data_dir: str, reports_dir: str, output_dir: str) -> None:
        self.data_dir = data_dir
        self.reports_dir = reports_dir
        self.output_dir = output_dir
        self.results: list[CompanyAnalyzeResults]
        self.logger = get_logger("sec_analyzer.analyzer")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(
            os.path.join(self.data_dir, "keywords.json"), "r", encoding="utf-8"
        ) as f:
            self.keywords: list[str] = json.load(f)
            self.combined_pattern = re.compile(
                r"|".join(
                    rf"\b{re.escape(word.lower())}\b" for word in self.keywords
                )
            )

    def analyze(self, companies: list[Company]) -> list["CompanyAnalyzeResults"]:
        self.logger.info(f"Starting analysis of {len(companies)} companies")
        with ThreadPoolExecutor() as executor:
            self.results = list(
                filter(None, executor.map(self.analyze_company, companies))
            )
        self.logger.info(f"Analysis completed for {len(self.results)} companies")

        return self.results

    def _results_to_df(self) -> pd.DataFrame:
        all_results = []
        all_results.sort(
            key=lambda x: (x["Company Name"], x["Year"], x["Report ID"])
        )
        for company_results in self.results:
            for result in company_results.results:
                entry = {
                    "Company Name": company_results.company.name,
                    "CIK": company_results.company.cik,
                    "Year": result.year,
                    "Accession number": result.accession_number,
                }
                entry.update(result.keyword_frequencies)
                all_results.append(entry)

        return pd.DataFrame(all_results)

    def save_results_to_excel(self):
        df = self._results_to_df()
        excel_path = os.path.join(self.output_dir, "sec_report_analysis_results.xlsx")
        df.to_excel(excel_path, index=False)
        self.logger.info(f"Results saved to Excel: {excel_path}")

    def save_results_to_csv(self):
        df = self._results_to_df()
        csv_path = os.path.join(self.output_dir, "sec_report_analysis_results.csv")
        df.to_csv(csv_path, index=False)
        self.logger.info(f"Results saved to CSV: {csv_path}")

    def analyze_company(self, company: Company) -> "CompanyAnalyzeResults":
        self.logger.info(f"Processing {company.name} ({company.cik})")
        company.download_reports(self.reports_dir, "2013-01-01")

        company_results = CompanyAnalyzeResults(company)

        for report_path in company.report_paths:
            try:
                report_result = self.analyze_report(report_path)
            except ValueError as e:
                error_message = f"{company.name} Skipping report {report_path} due to error: {e}"
                self.logger.error(error_message)
                continue
            except Exception as e:
                error_message = f"{company.name} Unexpected error processing {report_path}: {e}"
                self.logger.error(error_message)
                continue
            company_results.add_report_result(report_result)

        company.delete_reports()

        return company_results

    def analyze_report(
        self, file_path: str, save_debug_text: bool = False
    ) -> "ReportAnalyzeResult":
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()
            text = html.unescape(re.sub(r"<[^>]+>", "\n", content))
            text = re.sub(r"[ \xA0]+", " ", text).strip()
            text = re.sub(r"\n\s*", "\n", text) 

            if m := re.search(r"filed as of date:\s*(20\d{2})", text):
                year = int(m.group(1))
            elif m := re.search(r"filed:\s.*?(20\d{2})", text):
                year = int(m.group(1))
            else:
                raise Exception(f"year of report not found in file {file_path}")

            if m := re.search(r"accession\s*number:\s*(.*)\n", text):
                accession_number = m.group(1)
            else:
                accession_number = "unknown"

            if save_debug_text:
                unescaped_txt_path = os.path.join(self.output_dir, f"unescaped_{accession_number}.txt")
                with open(unescaped_txt_path, "w", encoding="utf-8") as output_file:
                    output_file.write(text)

            relevant_text = self._filter_relevant_text(text)
            if not relevant_text:
                raise ValueError(f"No relevant section found in file")
            
            if save_debug_text:
                relevant_text_path = os.path.join(self.output_dir, f"relevant_{accession_number}.txt")
                with open(relevant_text_path, "w", encoding="utf-8") as output_file:
                    output_file.write(relevant_text)

            matches = self.combined_pattern.findall(relevant_text)
            keyword_frequencies = {word: matches.count(word.lower()) for word in self.keywords}
            word_count = len(re.findall(r"\w+([-]\w+)*", relevant_text))

            return ReportAnalyzeResult(year, accession_number, word_count, keyword_frequencies)

    def _filter_relevant_text(self, text: str, min_length: int = 2500) -> str | None:
        start_patterns = [
            r"item:?1:?(descriptionof)?business:?\n",
            r"item:?1:?(descriptionof)?business:?",
            
        ]
        end_patterns = [
            r"item:?1:?a:?riskfactors:?\n",
            r"item:?1:?a:?riskfactors:?",
        ]
        
        for start_pattern in start_patterns:
            start_match = self._search_pattern(text, start_pattern)
            if start_match is None:
                continue

            for end_pattern in end_patterns:
                
                end_match = self._search_pattern(text[start_match.end():], end_pattern)
                if end_match is None:
                    continue

                section = text[start_match.end():start_match.end()+end_match.start()]
                if section and len(section) > min_length:
                    return section
        
        return None

    def _search_pattern(self, text: str, pattern: str) -> None | re.Match[str]:
        """Search for pattern in text and return the start position, or None if not found."""
        extended_pattern = r"".join(c + r"\s*" if (c.isalpha() or c.isnumeric()) else c for c in pattern)
        extended_pattern = re.sub(r':', r'[\.:‒–—―‐‑⁃−﹣－\-]', extended_pattern)
        extended_pattern = re.sub(r'([\)\]])(\?)?', r'\1\2\\s*', extended_pattern)

        self.logger.debug(f"Searching for pattern: {extended_pattern}")
        matches = list(re.finditer(extended_pattern, text, re.DOTALL))
        
        if len(matches) == 0:
            return None
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            return matches[1]


class CompanyAnalyzeResults:
    def __init__(self, company: Company):
        self.company = company
        self.results: list[ReportAnalyzeResult] = []

    def add_report_result(self, result: "ReportAnalyzeResult"):
        if self.of_year(result.year) is not None:
            raise ValueError(f"Results for year {result.year} already exist.")

        self.results.append(result)

    def of_year(self, year: int) -> "ReportAnalyzeResult | None":
        for result in self.results:
            if result.year == year:
                return result
        return None
    
    def __repr__(self) -> str:
        return f"CompanyAnalyzeResults(company={self.company.name}, results={self.results})"


class ReportAnalyzeResult:
    def __init__(self, year: int, accession_number: str, word_count: int, keyword_frequencies: dict[str, int]):
        self.year = year
        self.accession_number = accession_number
        self.word_count = word_count
        self.keyword_frequencies = keyword_frequencies

    def __repr__(self) -> str:
        return (
            f"ReportAnalyzeResult(year={self.year}, "
            f"accession_number='{self.accession_number}', "
            f"word_count={self.word_count}, "
            f"keyword_frequencies={self.keyword_frequencies})"
        )
