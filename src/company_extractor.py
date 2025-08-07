import os
import pandas as pd
import logging
from company import Company
from logger_config import get_logger


class CompanyExtractor:
    def __init__(self, data_dir: str, sheet_name: str = "Unternehmensliste Masterarbeit Mai 2025.xlsx") -> None:
        self.sheet_path = os.path.join(data_dir, sheet_name)
        self.logger = get_logger("sec_analyzer.extractor")


    def extract(self) -> list[Company]:
        self.logger.info(f"Starting company extraction from {self.sheet_path}")
        df = pd.read_excel(self.sheet_path, skiprows=3)

        companies: dict[str, Company] = {}

        for _, row in df.iterrows():
            company_name = row["conm"]
            cik = row["cik"]
            if cik is None or pd.isna(cik):
                continue

            cik = str(int(cik)).zfill(10)

            if companies.get(company_name) is None:
                company = Company(company_name, cik)
                companies[company_name] = company

        self.logger.info(f"Found {len(companies)} companies in the list")

        companies = {k: v for k, v in companies.items() if v.cik != "0000000nan"}

        self.logger.info(f"After filtering, {len(companies)} companies remain for analysis")
        return list(companies.values())