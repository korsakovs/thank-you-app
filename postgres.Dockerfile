FROM postgres:alpine
COPY ./docker/postgres/docker-entrypoint-initdb.d/* /docker-entrypoint-initdb.d/
