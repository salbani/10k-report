import html
import shutil
from typing import Any
from sec_edgar_downloader import Downloader
import os
import pandas as pd
import re
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, ".."))
data_dir = os.path.join(project_dir, "data")
output_dir = os.path.join(project_dir, "output")
filings_dir = os.path.join(project_dir, "sec-edgar-filings/")

# Load suchbegriffe from JSON file
with open(os.path.join(data_dir, "suchbegriffe.json"), "r", encoding="utf-8") as f:
    suchbegriffe: list[str] = json.load(f)


# Precompile the combined regex pattern for all suchbegriffe
combined_pattern = re.compile(r"|".join(rf"\b{re.escape(word.lower())}\b" for word in suchbegriffe))


# 📁 Pfad zu Apple-Berichten
report_folder = "10-K"
# Apple CIK
patterns = {
    word: re.compile(rf"\b{re.escape(word.lower())}\b") for word in suchbegriffe
}
# 🔁 Durchsuche jeden Bericht

class Company:
    def __init__(self, name: str, cik: str):
        self.name = name
        self.cik = cik
        self.years = []
        self.filings = []

    def add_filing(self, filing: Any):
        self.filings.append(filing)

    def add_year(self, year: str):
        if year not in self.years:
            self.years.append(year)

    def __repr__(self):
        return f"Company(name={self.name}, cik={self.cik}, filings={len(self.filings)})"
    


def process_file(company: Company, file_path: str) -> dict[str, Any] | None:
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().lower()
        text = html.unescape(re.sub(r'<[^>]+>', '', content))

        jahr = "Unbekannt"
        if (m := re.search(r"filed as of date:\s*(20\d{2})", content)):
            jahr = m.group(1)
        elif (m := re.search(r"filed:\s.*?(20\d{2})", content)):
            jahr = m.group(1)

        # Compile patterns locally (picklable-safe)
        eintrag = {"Unternehmen": company.name, "Jahr": jahr, "Bericht": file_path}

        # Count occurrences of all suchbegriffe in one pass
        matches = combined_pattern.findall(text)
        counts = {word: matches.count(word.lower()) for word in suchbegriffe}

        # Update eintrag with counts
        eintrag.update(counts)

        print(eintrag)
        return eintrag


def process_company(company: Company) -> list[dict[str, Any]]:
    print(f"Processing {company.name} ({company.cik})\n")
    dl = Downloader("sec-edgar-filings", "jaspeb97@zedat.fu-berlin.de")
    dl.get("10-K", company.cik, after="2013-01-01")

    entries = []

    for folder in os.listdir(os.path.join(filings_dir, company.cik, report_folder)):
        report_path = os.path.join(filings_dir, company.cik, report_folder, folder, "full-submission.txt")
        if not os.path.exists(report_path):
            print(f"File not found: {report_path}")
            continue
        entry = process_file(company, report_path)
        if entry is not None:
            entries.append(entry)
    
    # remove folder and files after processing
    shutil.rmtree(os.path.join(filings_dir, company.cik, report_folder))  
    return entries     



if __name__ == "__main__": 
    start_time = time.time()
    df = pd.read_excel(os.path.join(data_dir, "Unternehmensliste Masterarbeit Mai 2025.xlsx"), skiprows=3)

    companies: dict[str, Company] = {}

    for index, row in df.iterrows():
        company_name = row["conm"]
        cik = row["cik"]
        if cik is None or pd.isna(cik):
            continue

        cik = str(int(cik)).zfill(10)
        year = str(row["fyear"])

        if companies.get(company_name) is None:
            company = Company(company_name, cik)
            companies[company_name] = company
        else:
            company = companies[company_name]
            if cik == "0000000nan":
                print(f"CIK is NaN for {company_name} in year {year}")

        company.add_year(year)

    print(f"Found {len(companies)} companies in the list.")

    companies = {k: v for k, v in companies.items() if v.cik != "0000000nan"}
    # filter first 3 companies for testing
    companies = {k: v for k, v in list(companies.items())[:3]}
    print(len(companies))

    with ProcessPoolExecutor() as executor:
        ergebnisse = list(filter(None, executor.map(process_company, list(companies.values()))))

    shutil.rmtree(filings_dir)

    ergebnisse = [entry for sublist in ergebnisse for entry in sublist]

    print(f"Ergebnisse: {len(ergebnisse)} Einträge")

    # 🧾 In DataFrame umwandeln & als Excel speichern
    df = pd.DataFrame(ergebnisse)
    print(df.head())
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    df.to_excel(os.path.join(output_dir, "results.xlsx"), index=False)

    elapsed_time = time.time() - start_time
    print(f"Total running time: {elapsed_time:.2f} seconds")