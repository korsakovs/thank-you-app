FROM grafana/promtail:latest
RUN mkdir -p /etc/promtail
COPY ./docker/promtail/config.yaml /etc/promtail/
