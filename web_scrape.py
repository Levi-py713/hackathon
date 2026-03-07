import json
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

# Step 1: Open bCourses login
driver.get('https://bcourses.berkeley.edu')

# Step 2: Wait for YOU to log in manually (handles CAS + Duo 2FA)
print("Please log in manually in the browser window...")
WebDriverWait(driver, 120).until(EC.url_contains('https://bcourses.berkeley.edu'))
print("Logged in! Fetching courses via Canvas API...")

# Step 3: Hit the Canvas API directly
driver.get('https://bcourses.berkeley.edu/api/v1/courses?enrollment_state=active&per_page=50')
time.sleep(2)

# Step 4: Parse JSON
raw_text = driver.find_element(By.TAG_NAME, 'body').text
try:
    courses = json.loads(raw_text)
except json.JSONDecodeError:
    pre = driver.find_element(By.TAG_NAME, 'pre')
    courses = json.loads(pre.text)

print(f"Found {len(courses)} total courses")

# Step 5: Normalize each course code to a clean catalog code
def normalize(name):
    name = name.strip()

    # Remove suffixes like -LEC-001/002, -S26, SP26, -FL25, "Topic Reviews" etc.
    name = re.sub(r'[-\s]+(LEC|DIS|LAB|SEM|SP|FL|FA|SU|S|F)\w*[-\d/]*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*(Spring|Fall|Summer|Winter)\s*\d{4}.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*-\s*\d{3}.*$', '', name)
    name = re.sub(r'\s+Topic Reviews.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^SLC\s+', '', name, flags=re.IGNORECASE)  # strip "SLC " prefix
    name = name.strip()

    # Fix missing space in codes like CS61B → CS 61B, EE16A → EE 16A
    name = re.sub(r'^([A-Za-z]+)(\d)', r'\1 \2', name)

    # Uppercase
    name = name.upper()

    # Map known bCourses aliases to catalog codes
    aliases = {
        'EE 16A': 'EECS 16A',
        'EE 16B': 'EECS 16B',
    }
    return aliases.get(name, name)

# Step 6: Filter to only real academic courses
def is_academic(raw_name, normalized):
    # Must match: LETTERS + space + optional letters + NUMBER + optional letters
    # e.g. CS 61A, MATH 54, PHYSICS 7A, SLAVIC R5B
    if not re.match(r'^[A-Z]+(?:\s[A-Z]+)?\s[A-Z]?\d+[A-Z]?$', normalized):
        return False
    # Exclude known non-course patterns (but not SLC since we strip that above)
    skip_keywords = ['training', 'enrollment', 'signatory', 'partysafe', 'shape',
                     'supernode', 'gbo', 'gba', 'aod', 'vb']
    if any(kw in raw_name.lower() for kw in skip_keywords):
        return False
    return True

raw_names = [c.get('course_code') or c.get('name') or '' for c in courses]
results = []
for raw in raw_names:
    norm = normalize(raw)
    if is_academic(raw, norm):
        results.append(norm)
        print(f"  ✓ {raw!r:40} → {norm}")
    else:
        print(f"  ✗ skipped: {raw!r}")

print(f"\nFinal classes: {results}")

# Step 7: Save to JSON
output = {"classes": results, "raw": raw_names}
output_path = os.path.join(os.path.dirname(__file__), "user_classes.json")
with open(output_path, "w") as f:
    json.dump(output, f)

print(f"Done! Saved {len(results)} classes to {output_path}")
driver.quit()