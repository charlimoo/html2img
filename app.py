from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import io
import base64

app = Flask(__name__)

# Configure Chrome for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=800x600")
chrome_options.add_argument("--no-sandbox")

@app.route('/convert', methods=['POST'])
def convert_html_to_image():
    try:
        data = request.json
        html_content = data.get("html")
        width = data.get("width", 800)
        height = data.get("height", 600)

        if not html_content:
            return jsonify({"error": "Missing 'html' field"}), 400

        # Start headless Chrome
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(width, height)

        # Load HTML content
        driver.get("data:text/html;charset=utf-8," + html_content)

        # Take a screenshot (in-memory)
        screenshot = driver.get_screenshot_as_png()
        driver.quit()

        # Convert screenshot to base64
        image_base64 = base64.b64encode(screenshot).decode("utf-8")

        return jsonify({"image_base64": image_base64})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
