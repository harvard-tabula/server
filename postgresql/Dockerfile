FROM postgres:9.6
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD docker
ENV POSTGRES_DB docker
RUN apt-get update && apt-get install -y python3 python3-pip libpq-dev
ADD CreateDB.sql /docker-entrypoint-initdb.d/