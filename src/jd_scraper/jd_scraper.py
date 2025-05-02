# # EXAMPLE USAGE

# if __name__ == "__main__":
#     scraper = JobDescriptionScraper()
#     sampleURL = "https://www.linkedin.com/jobs/view/4197961513"
#     scraper.setInputs(sampleURL)
#     print(scraper.extractJobDescription())
#     scraper.resetScraper()


import requests
from bs4 import BeautifulSoup
import trafilatura
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import regex as re

class JobDescriptionScraper:
    def __init__(self):
        self.baseUrl = None
        self.jobDescription = ""
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/113.0.0.0 Safari/537.36"
            )
        }

        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = None

    def setInputs(self, baseUrl):
        if not isinstance(baseUrl, str):
            raise TypeError("baseUrl must be a string.")
        self.baseUrl = baseUrl
    
    def postProcessJDText(self, text):
        text = re.sub(r'\n+', '\n', text.strip())

        cutoff_phrases = [
            "Seniority level",
            "Referrals increase your chances",
            "People also viewed",
            "Similar jobs",
            "Explore collaborative articles",
        ]

        for phrase in cutoff_phrases:
            if phrase in text:
                text = text.split(phrase)[0].strip()
                break

        return text
    
    def extractJobDescription(self):
        self.driver = webdriver.Chrome(options=self.chrome_options)
        if self.jobDescription:
            return self.jobDescription
        if not self.baseUrl:
            raise ValueError("baseUrl must be set before extracting job description.")

        try:
            self.driver.get(self.baseUrl)
            time.sleep(1)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
        except Exception as e:
            raise RuntimeError(f"Error loading page: {e}")
        
        text = trafilatura.extract(self.driver.page_source)
        if text and len(text) > 200:
            self.jobDescription = self.postProcessJDText(text)
        
        self.driver.quit()
        
        return self.jobDescription

    def resetScraper(self):
        self.baseUrl = None
        self.jobDescription = ""
        if self.driver:
            self.driver.quit()
            self.driver = None


