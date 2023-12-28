FROM python:3.8-alpine AS merci-bot
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
WORKDIR /merci-bot
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "-m", "thankyou.slackbot"]
