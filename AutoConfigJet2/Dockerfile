From ubuntu:latest
MAINTAINER Vadim Sokolov 'sokolovadosolo@gmail.com'
RUN apt-get update -y
RUN apt-get install -y python3 python3-dev python3-pip build-essential
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ['python']
CMD ['app.py']
