FROM python:3.8-alpine AS merci-bot
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev
WORKDIR /merci-bot
COPY . .
RUN pip install -r requirements.txt
RUN mkdir -p /multiprocprometheus
CMD ["python", "-m", "thankyou.slackbot"]
