# website-screenshots-service
An API for generating screenshots for any website


Setup
-----

Build the docker image from the `Dockerfile` run

    docker build . --tag basicsvc2

To get a debugging/dev shell inside the container, run

    docker run \
      --cap-add SYS_ADMIN \
      -v $(pwd):/webapp \
      -p 5000:5000 \
      -it  basicsvc2 /bin/bash

Once inside the container you can generate a scneeshot using:

    chromium-browser --headless --disable-gpu --screenshot --window-size=1280,768 https://github.com/seanttaylor/biblio

then start a webserver 

    python3 -m http.server  5000
    
open your browser to http://localhost:5000 and find that screenshot!

