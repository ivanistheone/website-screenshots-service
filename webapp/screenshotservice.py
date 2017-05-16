#!/usr/bin/env python3

import boto3
from botocore.client import Config
from datetime import datetime
from flask import Flask, jsonify, request
import os
import shutil
from slugify import slugify
import subprocess
import sys
from urllib.parse import urlparse


# Require credentials from environment variables
if 'S3_AWS_ACCESS_KEY_ID' not in os.environ:
    print('Missing environment variable AWS_ACCESS_KEY_ID')
    sys.exit(1)
if 'S3_AWS_SECRET_ACCESS_KEY' not in os.environ:
    print('Missing environment variable AWS_SECRET_ACCESS_KEY')
    sys.exit(1)
S3_AWS_ACCESS_KEY_ID = os.environ['S3_AWS_ACCESS_KEY_ID']
S3_AWS_SECRET_ACCESS_KEY = os.environ['S3_AWS_SECRET_ACCESS_KEY']

S3_BUCKET_NAME = 'web-screenshot-service'
S3_BUCKET_BASE_URL = 'https://s3.ca-central-1.amazonaws.com/web-screenshot-service/'

WORKDIR = os.getcwd()

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
        screenshot_dir = screenshot_dir + '/' + subdir
    destination_path  = screenshot_dir + '/' + screenshot_name
    #
    #
    # A. Generate screenshot
    tmp_dir = os.path.join('/tmp', screenshot_dir)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    os.chdir(tmp_dir)
    cmd_template =  'chromium-browser --headless --disable-gpu --no-sandbox '
    cmd_template += '--screenshot --hide-scrollbars '
    cmd_template += '--window-size={window_width},{window_height} {website_url} '
    cmd = cmd_template.format(window_width=screenshot_width,
                              window_height=screenshot_height,
                              website_url=website_url)
    print('running:', cmd)
    chrome_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    chrome_process.wait()
    print(chrome_process.returncode)
    os.chdir(WORKDIR)
    screenshot_tmp_path = tmp_dir + '/screenshot.png'
    if not os.path.exists(screenshot_tmp_path):              # handle error case
        return jsonify({"status": "error",
                        "message": "Chrome failed to generate screnshot."})
    #
    # B. Upload to s3
    client = boto3.client(
        's3',
        aws_access_key_id=S3_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=S3_AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4')
    )
    screenshot_file = open(screenshot_tmp_path, 'rb')
    aws_resp = client.put_object(
        ACL = 'public-read',
        Bucket = S3_BUCKET_NAME,
        Key = destination_path,
        Body = screenshot_file,
        ContentType = 'image/png')
    print(aws_resp)
    resp_status = aws_resp['ResponseMetadata']['HTTPStatusCode']
    #
    # C. Remove local screenshot tmp file and containing dir
    shutil.rmtree(tmp_dir)
    #
    #
    if resp_status == 200:
        s3_url = S3_BUCKET_BASE_URL + destination_path
        return jsonify({"status": "success",
                        "screenshot_url": s3_url})
    else:
        return jsonify({"status": "error",
                        "message": "Uploading to s3 failed"})


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
