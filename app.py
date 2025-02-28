from flask import Flask, request, send_file, jsonify
from html2image import Html2Image
import os
import uuid

app = Flask(__name__)

# Ensure a temp directory exists for storing images
TEMP_DIR = "temp_images"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/convert', methods=['POST'])
def convert_html_to_image():
    try:
        data = request.json
        html_content = data.get("html")
        width = data.get("width", 800)  # Default width: 800px
        height = data.get("height", 600)  # Default height: 600px

        if not html_content:
            return jsonify({"error": "Missing 'html' field"}), 400

        # Generate a unique filename
        filename = f"{uuid.uuid4().hex}.png"
        image_path = os.path.join(TEMP_DIR, filename)

        # Convert HTML to image
        hti = Html2Image(output_path=TEMP_DIR)
        hti.screenshot(html_str=html_content, save_as=filename, size=(width, height))

        # Return the image
        return send_file(image_path, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
