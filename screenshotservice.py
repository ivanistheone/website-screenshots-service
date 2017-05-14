#!/usr/bin/env python3

import boto3
from botocore.client import Config
from datetime import datetime
from flask import Flask, jsonify, request
import os
from slugify import slugify
import subprocess
import sys
from urllib.parse import urlparse



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
S3_SCREENSHOTS_BUCKET_BASE_URL = 'https://s3.ca-central-1.amazonaws.com/web-screenshot-service/'


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Flask Dockerized'


@app.route('/api/webscreehsot/', methods=['POST'])
def web_screenshot():
    """
    Expects HTTP POST requests with JSON pauload of the form:

        { "website_url": "https://www.nytimes.com/",
          "window_width": 1048,
          "window_height": 768 }
    
    Returns a link to the website screenshot url (hosted on s3)
    
        { "status": "success",
          "screenshot_url": "http://s3bucket.region.amazonaws.com/...shot.png" }
    
    """
    data = request.get_json()
    print('received POST data', data)
    website_url = data['website_url']
    screenshot_width = data.get('window_width', 1048)
    screenshot_height =  data.get('window_height', 768)
    #
    #
    # Prepare containing folder, subfolder, and screenshot name with timestamp
    parsed_uri = urlparse(website_url)
    domain = parsed_uri.netloc
    screenshot_dir = domain.replace('.', '_')     # www_nytimes_com
    subdir = slugify(str(parsed_uri.path.lstrip('/'))) # 2017_05_13_worl...ariclehtml
    screenshot_name = 'screenshot' + datetime.now().strftime('%Y%M%d_%H%M%S') + '.png'
    if subdir:
        screenshot_path = screenshot_dir + '/' + subdir + '/' + screenshot_name
    else:
        screenshot_path = screenshot_dir + '/' + screenshot_name
    #
    #
    # A. Generate screenshot
    cmd_template =  'chromium-browser --headless --disable-gpu --screenshot '
    cmd_template += '--window-size={window_width},{window_height} {website_url}'
    cmd = cmd_template.format(window_width=screenshot_width,
                              window_height=screenshot_height,
                              website_url=website_url)
    print('running:', cmd)
    # chrome_process = subprocess.Popen(cmd, stdout=sp.PIPE)
    # chrome_process.wait()
    # print(chrome_process.returncode)
    # TODO: handle error case
    #
    # B. Upload to s3
    client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4')
    )
    screenshot_file = open('screenshot.png', 'rb')
    aws_resp = client.put_object(
        ACL = 'public-read',
        Bucket = S3_SCREENSHOTS_BUCKET_NAME,
        Key = screenshot_path,
        Body = screenshot_file)
    print(aws_resp)
    resp_status = aws_resp['ResponseMetadata']['HTTPStatusCode']
    #
    # C. Return screenshot url
    if resp_status == 200:
        s3_url = S3_SCREENSHOTS_BUCKET_BASE_URL + screenshot_path
        return jsonify({"status": "success",
                        "screenshot_url": s3_url})
    else:
        return jsonify({"status": "error",
                        "message": "Uploading to s3 failed"})


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
