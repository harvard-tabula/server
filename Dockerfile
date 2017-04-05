FROM ubuntu:16.04

RUN apt-get update && apt-get install -y python3 python3-pip libpq-dev nginx uwsgi vim

COPY . /var/www

WORKDIR /var/www

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default
ADD sites-enabled/ /etc/nginx/sites-enabled

COPY certificate.pem /certs/certificate.pem
COPY key.key /certs/key.key
RUN rm certificate.pem; rm key.key

EXPOSE 80
EXPOSE 443

# Use the below for a slightly more lightweight debugging experience locally.
RUN pip3 install -e ./web
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]

# Use this for prod
#CMD ["uwsgi", "--socket", "0.0.0.0:8000", "--protocol=http", "--wsgi-file", "/var/www/web/wsgi.py", "--callable", "app", "--logto", "/var/log/uwsgi.log", "--py-autoreload", "1"]
