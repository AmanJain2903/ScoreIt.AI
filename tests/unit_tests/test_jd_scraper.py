import pytest
from unittest.mock import patch, MagicMock
from src.jd_scraper.jd_scraper import JobDescriptionScraper
import numpy as np

pytestmark = pytest.mark.unit

@pytest.fixture
def mock_driver():
    with patch("src.jd_scraper.jd_scraper.webdriver.Chrome") as mock_chrome:
        mock_instance = MagicMock()
        mock_instance.page_source = "<html><body>Sample Job Description</body></html>"
        mock_chrome.return_value = mock_instance
        yield mock_chrome


@pytest.fixture
def mock_trafilatura():
    with patch("src.jd_scraper.jd_scraper.trafilatura") as mock_traf:
        mock_traf.extract.return_value = "Sample Job Description " * 20
        yield mock_traf

@pytest.fixture
def mock_beautifulsoup():
    with patch("src.jd_scraper.jd_scraper.BeautifulSoup") as mock_bs:
        mock_bs.return_value = MagicMock()
        yield mock_bs

@pytest.fixture
def jd_scraper(mock_driver, mock_trafilatura):
    return JobDescriptionScraper()

def test_initialization(jd_scraper):
    assert jd_scraper.baseUrl is None
    assert jd_scraper.jobDescription == ""
    assert jd_scraper.driver is None
    assert jd_scraper.chrome_options is not None
    assert jd_scraper.headers == {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/113.0.0.0 Safari/537.36"
            )
        }

def test_setInputs_success(jd_scraper):
    baseUrl = "https://example.com/job"
    jd_scraper.setInputs(baseUrl)
    assert jd_scraper.baseUrl == baseUrl

def test_setInputs_invalid_type(jd_scraper):
    with pytest.raises(TypeError, match="baseUrl must be a string."):
        jd_scraper.setInputs(123)

def test_postProcessJDText(jd_scraper):
    text = "Sample Job Description\n\nSeniority level: Senior\n\nReferrals increase your chances"
    processed_text = jd_scraper.postProcessJDText(text)
    assert processed_text == "Sample Job Description"

def test_extractJobDescription_success(jd_scraper, mock_driver, mock_beautifulsoup, mock_trafilatura):
    baseUrl = "https://example.com/job"
    jd_scraper.setInputs(baseUrl)
    job_description = jd_scraper.extractJobDescription()
    assert job_description == jd_scraper.postProcessJDText("Sample Job Description " * 20)

def test_extractJobDescription_no_baseUrl(jd_scraper):
    with pytest.raises(ValueError, match="baseUrl must be set before extracting job description."):
        jd_scraper.extractJobDescription()

def test_extractJobDescription_already_job_description(jd_scraper, mock_driver):
    baseUrl = "https://example.com/job"
    jd_scraper.setInputs(baseUrl)
    jd_scraper.jobDescription = "Sample Job Description " * 20
    job_description = jd_scraper.extractJobDescription()
    assert job_description == "Sample Job Description " * 20
    mock_driver.return_value.get.assert_not_called()
    mock_driver.return_value.quit.assert_not_called()

def test_extractJobDescription_failed(jd_scraper, mock_driver):
    with patch("src.jd_scraper.jd_scraper.webdriver.Chrome") as mock_chrome:
        mock_driver_instance = MagicMock()
        mock_driver_instance.get.side_effect = Exception("Failed to load page")
        mock_chrome.return_value = mock_driver_instance

        scraper = JobDescriptionScraper()
        scraper.setInputs("https://example.com/job")

        with pytest.raises(RuntimeError, match="Error loading page: Failed to load page"):
            scraper.extractJobDescription()

def test_resetScraper(jd_scraper):
    baseUrl = "https://example.com/job"
    jd_scraper.setInputs(baseUrl)
    jd_scraper.jobDescription = "Sample Job Description"
    jd_scraper.driver = MagicMock()
    jd_scraper.resetScraper()
    assert jd_scraper.baseUrl is None
    assert jd_scraper.jobDescription == ""
    assert jd_scraper.driver is None

    