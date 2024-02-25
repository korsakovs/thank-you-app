FROM python:3.8-alpine AS merci-bot
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev
WORKDIR /merci-bot
COPY . .
RUN pip install -r requirements.txt
RUN mkdir -p /multiprocprometheus
CMD ["gunicorn", \
        "--worker-class=sync", \
        "--worker-connections=100", \
        "--workers", "10", \
        "--bind", "unix:/nginx_sockets/merci_bot.sock", \
        "--config=thankyou/slackbot/utils/gunicorn_conf.py", \
    "thankyou.slackbot.utils.wsgi:slack_app()"]
