from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

# Step 1: Open CalCentral login
driver.get('https://bcourses.berkeley.edu')

# Step 2: Wait for YOU to log in manually (handles CAS + Duo 2FA)
print("Please log in manually in the browser window...")
WebDriverWait(driver, 120).until(EC.url_contains('https://bcourses.berkeley.edu'))
print("Logged in! Scraping now...")

# Step 3: Scrape page
driver.get('https://bcourses.berkeley.edu/')  # change to your target page

soup = BeautifulSoup(driver.page_source, 'html.parser')

#Creates empty list of names
classes = []
for x in soup.find_all(class_='ic-DashboardCard'):
    class_name = x['aria-label']
    classes = classes + [class_name]
        
print(classes)






# Step 4: Do your scraping here
# e.g. find elements, extract text, etc.

driver.quit()