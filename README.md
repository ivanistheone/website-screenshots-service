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



AWS credentials
---------------
The commands depend on two IAM users existing in AWS and their associated credentials
being available as environment variables.

Credentials for a user with full `s3` read/write access, available as:

    S3_AWS_ACCESS_KEY_ID  and     S3_AWS_SECRET_ACCESS_KEY

See step-by-step screenshots in `docs/aws_steps/create_s3_user/`.

Credentials with [full `ec2` and `VPC` access](docs/docker_machine_user_IAM_policy.txt)
for use by docker machine, provided as the environment variables

    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY

For convenience, you can create an `.env` file in the directory `credentials/`
to store all four environment variables. For example `credentials/aws-keys.env`
should contain:

    export S3_AWS_ACCESS_KEY_ID=12i8u3n23ni
    export S3_AWS_SECRET_ACCESS_KEY=2oi3jnsdlcknsdvjnsdonvosfdinvosnv
    export AWS_ACCESS_KEY_ID=232384i84
    export AWS_SECRET_ACCESS_KEY=asoijadmscio9i4940dpsdlsidjsoidjji

and all variables can be loaded into the current shell environment using

    source credentials/aws-keys.env


S3 Bucket
---------
The website screenshot service uses an s3 bucket to store the generates images.
The instructions below assume the s3 bucket is called `web-screenshot-service`
and it is created in the `ca-central-1` AWS region. Files stored in this bucket
will be served at this path `https://s3.ca-central-1.amazonaws.com/web-screenshot-service/`.

Follow the step step-by-step instructions in `docs/aws_steps/create_s3_bucket/`.



Running locally
---------------
Build the docker image from the `Dockerfile` run

    docker build . --tag screenshot-docker-img

To get a debugging/dev shell inside the container, run

    docker run \
      -v webapp:/webapp \
      -p 5000:5000 \
      -e S3_AWS_ACCESS_KEY_ID=$S3_AWS_ACCESS_KEY_ID \
      -e S3_AWS_SECRET_ACCESS_KEY=$S3_AWS_SECRET_ACCESS_KEY \
      -e S3_BUCKET_NAME="web-screenshot-service" \
      -e S3_BUCKET_BASE_URL="https://s3.ca-central-1.amazonaws.com/web-screenshot-service/" \
      -it screenshot-docker-img  /bin/bash


Once inside the container, `cd /webapp` then run `python3 screenshotservice.py`.



Running in production
---------------------
We'll use the command line tool `docker-machine` for the following two tasks:
  - Provision an `ec2` instance (a virtual machine rented from AWS) which will
    serve as the docker host
  - Confiture 
  

### Creating the docker host on AWS

Use `docker-machine` to setup a docker host called `awsdhost` in the AWS cloud

    docker-machine create -d amazonec2 \
        --amazonec2-region ca-central-1 \
        --amazonec2-zone b \    
        awsdhost

Note this command depends on the env variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
for the `docker-machine-user` IAM role being present in the environment.
Use the `--amazonec2-region` option `us-east-1` to provision a host close to NYC.

Assuming everything goes to plan, a new `t1.micro` instance should be running,
with docker installed on it and the docker daemon listening on port `2375`.

The settings required to configure docker to build and deploy containers can be
displayed using the command:

      docker-machine env awsdhost



### Using docker on the dockerhost

In order to configure docker to build and run containers on `awsdhost`, we must
inject the appropriate env variables which will tell the local docker command
where it should work:

      eval $(docker-machine env awsdhost)

After running this command we must build the docker image on `awshost`:

    docker build . --tag screenshot-docker-img

Before we run the container, make sure the env contains the S3 credentials by
running `source credentials/aws-keys.env` if needed.

To start the container from the image tagged `screenshot-docker-img` on `awshost`,
run the following command:

    docker run \
      -p 5000:5000 \
      -e S3_AWS_ACCESS_KEY_ID=$S3_AWS_ACCESS_KEY_ID \
      -e S3_AWS_SECRET_ACCESS_KEY=$S3_AWS_SECRET_ACCESS_KEY \
      -e S3_BUCKET_NAME="web-screenshot-service" \
      -e S3_BUCKET_BASE_URL="https://s3.ca-central-1.amazonaws.com/web-screenshot-service/" \
      -d screenshot-docker-img

Make sure `S3_BUCKET_NAME` and `S3_BUCKET_BASE_URL` are set appropriately.

This will run the entry CMD `python3 screenshotservice.py` to start the service.


### Open port 5000

May be necessary to go to security rules for the instance (default security group)
and allow access to port 5000.





Shutting down
-------------

To stop the container:

    eval $(docker-machine env awsdhost)
    docker ps                     # to find the container ID
    docker stop <container_id>

To destroy the machine:

    source credentials/aws-keys.env
    docker-machine rm awsdhost

