FROM python:3.8-alpine AS merci-bot
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev
WORKDIR /merci-bot
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "--worker-class=sync", "--worker-connections=100", "--workers", "5", "--bind", "unix:/nginx_sockets/merci_bot.sock", "thankyou.slackbot.utils.wsgi:slack_app()"]
