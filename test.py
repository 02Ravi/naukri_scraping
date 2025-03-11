from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import time
import random
import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# Configure Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-popup-blocking")
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)

# Create DataFrame to store scraped data
dff = pd.DataFrame(columns=['Job Title', 'Description', 'Experience Reqd', 'Company', 'City', 'Salary Range', 'Date Posted', 'URL'])

# Loop through pages 0 to 200
for page in range(0, 200): 
    url = f"https://www.naukri.com/ai-jobs-{page}?k=ai"
    driver.get(url)

    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'listContainer')))
    except:
        print(f"Skipping page {page} (No job listings found).")
        continue

    soup = BeautifulSoup(driver.page_source, 'html5lib')
    results = soup.find(id='listContainer')

    if results:
        job_elems = results.find_all('div', class_='srp-jobtuple-wrapper')

        for job_elem in job_elems:
            Title = job_elem.find('a', class_='title')
            Title = Title.text.strip() if Title else "Not Available"

            Description = job_elem.find('span', class_='job-desc')
            Description = Description.text.strip() if Description else "Not Available"

            Exp = job_elem.find('span', class_='expwdth')
            Exp = Exp.text.strip() if Exp else "Not Mentioned"

            Company = job_elem.find('a', class_='comp-name')
            Company = Company.text.strip() if Company else "Not Available"

            City = job_elem.find('span', class_='locWdth')
            City = City.text.strip() if City else "Not Available"

            Salary = job_elem.find('span', class_='ni-job-tuple-icon ni-job-tuple-icon-srp-rupee sal')
            Salary = Salary.text.strip() if Salary else "Not Mentioned"

            Date = job_elem.find('span', class_='job-post-day')
            Date = Date.text.strip() if Date else "Not Available"

            URL = job_elem.find('a', class_='title')
            URL = URL['href'] if URL else "Not Available"

            dff = pd.concat([dff, pd.DataFrame([[Title, Description, Exp, Company, City, Salary, Date, URL]],
                                               columns=['Job Title', 'Description', 'Experience Reqd', 'Company', 'City', 'Salary Range', 'Date Posted', 'URL'])],
                            ignore_index=True)

    print(f"Scraped Page {page}")

# Save scraped data to Excel
os.makedirs("data", exist_ok=True)
file_name = f"data/NaukriJobListing_{datetime.today().date()}.xlsx"
dff.to_excel(file_name, index=False)

print(f"Scraping completed. Data saved to {file_name}")

# Close the browser
driver.quit()
