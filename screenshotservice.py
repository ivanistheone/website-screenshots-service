import boto3
from datetime import datetime
from flask import Flask, jsonify
import os
import subprocess
import sys
from urlparse import urlparse


# Load credentials from environment variables
if 'AWS_ACCESS_KEY_ID' not in os.environ:
    print('Missing environment variable AWS_ACCESS_KEY_ID')
    sys.exit(1)
if 'AWS_SECRET_ACCESS_KEY' not in os.environ:
    print('Missing environment variable AWS_SECRET_ACCESS_KEY')
    sys.exit(1)
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

S3_SCREENSHOTS_BUCKET_NAME = 'web-screenshot-service'


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Flask Dockerized'


@app.route('/api/webscreehsot/', methods=['POST']))
def web_screenshot():
    """
    Expects HTTP POST requests with JSON pauload of the form:

        { "website_url":"https://www.nytimes.com/",
          "window_width": 1048,
          "window_height": 768 }
    
    Returns a link to the website screenshot url (hosted on s3)
    
        { "status": "success",
          "screenshot_url": "http://s3bucket.region.amazonaws.com/...shot.png" }
    
    """
    data = request.get_json()
    print('received POST data', data)
    website_url = data['uwebsite_urlrl']
    screenshot_width = data.get('window_width', 1048)
    screenshot_height =  data.get('window_height', 768)
    #
    #
    # Prepare screenshot name and containing folder
    parsed_uri = urlparse(website_url)
    domain = parsed_uri.netloc
    screenshot_dir = domain.replace('.', '_')
    screenshot_name = 'screenshot' + datetime.now().strftime('%Y%M%d_%H%M') + '.png'
    #
    #
    # A. Generate screenshot
    cmd_template =  'chromium-browser --headless --disable-gpu --screenshot '
    cmd_template += '--window-size={window_width},{window_height} {website_url}'
    cmd = cmd_template.format(window_width=window_width,
                              window_height=window_height,
                              website_url=website_url)
    chrome_process = subprocess.Popen(cmd, stdout=sp.PIPE)
    chrome_process.wait()
    print(chrome_process.returncode)
    # TODO: handle error case
    #
    # B. Upload to s3
    client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )
    screenshot_file = open('screenshot.png', 'rb')
    aws_resp = client.put_object(
        ACL = 'public-read',
        Bucket = S3_SCREENSHOTS_BUCKET_NAME,
        Key = screenshot_dir + '/' + screenshot_name,
        Body = screenshot_file)
    print(aws_resp)
    s3_url = 'asas'
    #
    #
    # C. Return screenshot url
    return jsonify({"status": "success",
                    "screenshot_url": s3_url})


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
