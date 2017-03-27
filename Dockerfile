FROM ubuntu:16.04

RUN apt-get update && apt-get install -y python3 python3-pip libpq-dev nginx uwsgi vim

COPY ./web/requirements.txt /var/www/requirements.txt
WORKDIR /var/www
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /var/www

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default
ADD sites-enabled/ /etc/nginx/sites-enabled

COPY certificate.pem /certs/certificate.pem
COPY key.key /certs/key.key
RUN rm certificate.pem; rm key.key

EXPOSE 80
EXPOSE 8080
EXPOSE 443

CMD ["uwsgi", "--socket", "0.0.0.0:8000", "--protocol=http", "--wsgi-file", "/var/www/web/application.py", "--callable", "app", "--logto", "/tmp/mylog.log"]
CMD ["nginx"]
