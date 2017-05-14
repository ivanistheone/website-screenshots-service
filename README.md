Website Screenshots Service
===========================
An API for generating screenshots for any website


TODO
----

  - Change to accept HTTP GET
  - Change url param names
  - Resize image using PIL, see http://pillow.readthedocs.io/en/3.1.x/reference/Image.html#PIL.Image.Image.resize
  - Return 302 to actual image instead of json
  - Deploy on docker-machine
    - ENV vars?
  - Deploy to `miniref-web1`



Idea
----
We want a service to generate website screenshots of any website or url.

example request:

    HTTP POST  /api/webscreehsot/
    { "website_url":"https://www.nytimes.com/",
      "window_width": 1048,
      "window_height": 768 }

response:

    { "status": "success",
      "screenshot_url": "http://bucket.s3-aws-region.amazonaws.com/nytimes/scrrenshot20170502.png" }


Setup
-----
Build the docker image from the `Dockerfile` run

    docker build . --tag basicsvc5

To get a debugging/dev shell inside the container, run

    docker run \
      -v $(pwd):/webapp \
      -p 5000:5000 \
      -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
      -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
      -it basicsvc5 /bin/bash



Production
----------

    docker run \
      -p 5000:5000 \
      -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
      -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
      -d basicsvc5

This will run the entry CMD `python3 screenshotservice.py` to start the service.


