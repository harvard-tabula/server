FROM tutum/nginx
COPY ./sites_enabled /var/www/sites_enabled
RUN rm /etc/nginx/sites-enabled/default
ADD sites-enabled/ /etc/nginx/sites-enabled