FROM python:3.8-alpine AS merci-webapp
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev
WORKDIR /merci-webapp
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "--worker-class=sync", "--worker-connections=100", "--workers", "5", "--bind", "unix:/nginx_sockets/merci_webapp.sock", "thankyou.webapp.app:wsgi()"]
