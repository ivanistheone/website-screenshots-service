from ubuntu:latest

# Install base
RUN apt-get update -y
RUN apt-get install -y software-properties-common python-software-properties


# Install chromium beta
RUN add-apt-repository -y ppa:saiarcot895/chromium-beta
RUN apt-get install -y chromium-browser


# Install python app & depends
RUN apt-get install -y python-pip python-dev build-essential
# RUN pip install -r requirements.txt


# COPY . /app
# WORKDIR /app

# CMD ["app.py"]