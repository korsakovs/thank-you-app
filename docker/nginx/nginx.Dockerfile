FROM nginx:latest

WORKDIR /usr/share/nginx/html
RUN rm -rf ./*

RUN mkdir -p /etc/nginx/sites-available
RUN mkdir -p /etc/nginx/sites-enabled
COPY ./docker/nginx/nginx.conf /etc/nginx/
COPY ./docker/nginx/sites/merci.bot /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/merci.bot /etc/nginx/sites-enabled/merci.bot
RUN cat /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]
