from ubuntu:latest

# Basic env setup  (credentials AWS_ACCESS... must be passed in at runtime)
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND noninteractive


# Install base
RUN apt-get update -y
RUN apt-get install -y software-properties-common python-software-properties


# Install chromium beta
RUN add-apt-repository -y ppa:saiarcot895/chromium-beta
RUN apt-get install -y chromium-browser


# Install python app & depends
RUN apt-get install -y python3-pip python3-dev build-essential
COPY webapp /webapp
RUN cd /webapp \
  && pip3 install -r requirements.txt

# EXPOSE 5000

WORKDIR /webapp
CMD python3 screenshotservice.py