FROM ubuntu:16.04
EXPOSE 8080

# set environment variables
ENV FLASK_APP ./web/application.py
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# install dependencies
RUN apt-get update && apt-get install -y python3 python3-pip libpq-dev

COPY ./web/requirements.txt /var/www/requirements.txt
WORKDIR /var/www
RUN pip3 install -r requirements.txt
COPY . /var/www

# start server inside container
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
