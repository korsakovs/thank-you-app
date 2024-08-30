FROM prom/prometheus
RUN mkdir -p /etc/prometheus/
COPY ./docker/prometheus/prometheus.yml /etc/prometheus/
ARG GRAFANA_COM_API_TOKEN
RUN echo ${GRAFANA_COM_API_TOKEN} > /etc/prometheus/password_file
