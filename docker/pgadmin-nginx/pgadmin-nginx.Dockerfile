FROM nginx:latest

WORKDIR /usr/share/nginx/html
RUN rm -rf ./*

RUN mkdir -p /etc/nginx/sites-available
RUN mkdir -p /etc/nginx/sites-enabled
COPY ./docker/pgadmin-nginx/nginx.conf /etc/nginx/
COPY ./docker/pgadmin-nginx/.htpasswd /etc/nginx/
COPY ./docker/pgadmin-nginx/sites/pgadmin /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/pgadmin /etc/nginx/sites-enabled/pgadmin

CMD ["nginx", "-g", "daemon off;"]
