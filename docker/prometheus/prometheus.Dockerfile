FROM prom/prometheus
RUN mkdir -p /etc/prometheus/
COPY ./docker/prometheus/prometheus.yml /etc/prometheus/
