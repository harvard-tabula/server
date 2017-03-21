FROM ubuntu:16.04
EXPOSE 8080

RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get install -y libpq-dev

COPY ./web/requirements.txt /var/www/requirements.txt
WORKDIR /var/www
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /var/www

# start server inside container
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
