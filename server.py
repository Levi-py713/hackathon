"""
StudyLink local scraper server.
Run this once before using the website:
    pip install flask flask-cors selenium
    python server.py
Then open http://localhost:8080/studylink.html as normal.
When you click Sign In, this server opens bCourses automatically.
"""

import json
import os
import re
import time
from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__, static_folder=os.path.dirname(os.path.abspath(__file__)), static_url_path='')
CORS(app, origins=["http://127.0.0.1:5001", "http://localhost:5000"])  # allow the website to call this server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def normalize(name):
    name = name.strip()
    name = re.sub(r'[-\s]+(LEC|DIS|LAB|SEM|SP|FL|FA|SU|S|F)\w*[-\d/]*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*(Spring|Fall|Summer|Winter)\s*\d{4}.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*-\s*\d{3}.*$', '', name)
    name = re.sub(r'\s+Topic Reviews.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^SLC\s+', '', name, flags=re.IGNORECASE)
    name = name.strip()
    name = re.sub(r'^([A-Za-z]+)(\d)', r'\1 \2', name)
    name = name.upper()
    aliases = {'EE 16A': 'EECS 16A', 'EE 16B': 'EECS 16B'}
    return aliases.get(name, name)

def is_academic(raw_name, normalized):
    if not re.match(r'^[A-Z]+(?:\s[A-Z]+)?\s[A-Z]?\d+[A-Z]?$', normalized):
        return False
    skip_keywords = ['training', 'enrollment', 'signatory', 'partysafe', 'shape',
                     'supernode', 'gbo', 'gba', 'aod', 'vb']
    if any(kw in raw_name.lower() for kw in skip_keywords):
        return False
    return True

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        print("\n[StudyLink] Starting bCourses scrape...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        # Open bCourses — user logs in manually
        driver.get('https://bcourses.berkeley.edu')
        print("[StudyLink] Browser opened. Waiting for user to log in (2 min)...")

        WebDriverWait(driver, 120).until(EC.url_contains('https://bcourses.berkeley.edu'))
        print("[StudyLink] Logged in! Fetching courses...")

        # Hit Canvas API
        driver.get('https://bcourses.berkeley.edu/api/v1/courses?enrollment_state=active&per_page=50')
        time.sleep(2)

        raw_text = driver.find_element(By.TAG_NAME, 'body').text
        try:
            courses = json.loads(raw_text)
        except json.JSONDecodeError:
            pre = driver.find_element(By.TAG_NAME, 'pre')
            courses = json.loads(pre.text)

        driver.quit()

        # Normalize and filter
        raw_names = [c.get('course_code') or c.get('name') or '' for c in courses]
        results = []
        for raw in raw_names:
            norm = normalize(raw)
            if is_academic(raw, norm):
                results.append(norm)
                print(f"  ✓ {raw!r} → {norm}")
            else:
                print(f"  ✗ skipped: {raw!r}")

        # Save JSON for fallback
        output = {"classes": results, "raw": raw_names}
        with open(os.path.join(BASE_DIR, "user_classes.json"), "w") as f:
            json.dump(output, f)

        print(f"[StudyLink] Done! Found {len(results)} classes: {results}")
        return jsonify(output)

    except Exception as e:
        print(f"[StudyLink] Error: {e}")
        return jsonify({"error": str(e), "classes": [], "raw": []}), 500

# Also serve the static files (HTML, JSON) so you only need one server
@app.route('/')
def index():
    return app.send_static_file('studylink.html')

if __name__ == '__main__':
    print("=" * 50)
    print("StudyLink server running.")
    print("Open http://localhost:5001 in your browser.")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)