from flask import Flask, request, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

app = Flask(__name__)

# Ensure the static directory exists
if not os.path.exists('static'):
    os.makedirs('static')

# HTML template for the web form
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Visitor</title>
</head>
<body>
    <h1>Enter URL to Visit</h1>
    <form method="post" action="/visit">
        <label for="url">URL:</label>
        <input type="text" id="url" name="url" required>
        <br>
        <label for="count">Number of Visits:</label>
        <input type="number" id="count" name="count" min="1" value="1" required>
        <br>
        <button type="submit">Visit</button>
    </form>
    <div>{{ result }}</div>
    <div>
        {% if screenshots %}
            <h2>Screenshots</h2>
            {% for screenshot in screenshots %}
                <img src="{{ screenshot }}" alt="Screenshot" style="max-width: 100%; height: auto;">
            {% endfor %}
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, result='', screenshots=[])

@app.route('/visit', methods=['POST'])
def visit():
    url = request.form.get('url')
    visit_count = int(request.form.get('count', 1))
    result = ''
    screenshots = []

    if not url or visit_count < 1:
        result = 'Valid URL and visit count are required.'
        return render_template_string(HTML_TEMPLATE, result=result, screenshots=screenshots)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9222')
    options.binary_location = "/usr/bin/google-chrome"  # Ensure this is the correct path

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        for i in range(visit_count):
            driver.get(url)
            time.sleep(3)

            screenshot_path = f'static/screenshot-{i + 1}-{int(time.time())}.png'
            driver.save_screenshot(screenshot_path)
            screenshots.append(screenshot_path)
        result = f'Completed {visit_count} visits successfully.'
    except Exception as e:
        result = f'Error during visits: {str(e)}'
    finally:
        if driver:
            driver.quit()

    return render_template_string(HTML_TEMPLATE, result=result, screenshots=screenshots)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
