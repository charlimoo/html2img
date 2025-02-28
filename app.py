from flask import Flask, request, jsonify
from html2image import Html2Image
from PIL import Image
import io
import base64
import uuid

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_html_to_image():
    try:
        data = request.json
        html_content = data.get("html")
        width = data.get("width", 800)  # Default width: 800px
        height = data.get("height", 600)  # Default height: 600px

        if not html_content:
            return jsonify({"error": "Missing 'html' field"}), 400

        # Generate a unique filename in memory
        filename = f"{uuid.uuid4().hex}.png"

        # Convert HTML to image (temporary file stored in RAM)
        hti = Html2Image(browser="chrome")
        temp_path = hti.screenshot(html_str=html_content, save_as=filename, size=(width, height))

        # Read the image into memory
        with open(temp_path[0], "rb") as image_file:
            image_bytes = image_file.read()

        # Convert to Base64
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        return jsonify({"image_base64": image_base64})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
