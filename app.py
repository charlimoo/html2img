from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import base64
import time

app = Flask(__name__)

# Configure Chrome for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # New headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--remote-allow-origins=*")

def clean_html(html):
    """Parses and fixes broken HTML using BeautifulSoup."""
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Ensure HTML, HEAD, and BODY exist
        if not soup.head:
            soup.insert(0, soup.new_tag("head"))
        if not soup.body:
            body_tag = soup.new_tag("body")
            body_tag.extend(soup.contents)
            soup.insert(len(soup.contents), body_tag)

        # Force UTF-8 meta tag if missing
        if not soup.head.find("meta", attrs={"charset": True}):
            meta_tag = soup.new_tag("meta", charset="utf-8")
            soup.head.insert(0, meta_tag)

        return str(soup)
    
    except Exception as e:
        return html  # If cleanup fails, return the raw HTML

@app.route('/convert', methods=['POST'])
def convert_html_to_image():
    try:
        data = request.json
        html_content = data.get("html", "")
        capture_id = data.get("capture_id", "capture-area")  # Default ID to look for

        if not html_content:
            return jsonify({"error": "Missing 'html' field"}), 400

        # Clean and fix broken HTML
        fixed_html = clean_html(html_content)

        # Start headless Chrome
        driver = webdriver.Chrome(options=chrome_options)

        # Load a blank page first
        driver.get("data:text/html;charset=utf-8,<html><body></body></html>")

        # Inject the cleaned HTML via JavaScript
        driver.execute_script("""
            document.open();
            document.write(arguments[0]);
            document.close();
        """, fixed_html)

        # Wait for styles, fonts, and images to load
        time.sleep(2)

        # Locate the target div by its ID
        element = driver.find_element("id", capture_id)

        if element:
            # Take a screenshot of only that element
            screenshot = element.screenshot_as_png
        else:
            # Fallback: Take a full-page screenshot if element not found
            screenshot = driver.get_screenshot_as_png()

        driver.quit()

        # Convert screenshot to base64
        image_base64 = base64.b64encode(screenshot).decode("utf-8")

        return jsonify({"image_base64": image_base64})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
