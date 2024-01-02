#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE USER "$SLACK_APP_POSTGRES_USERNAME" WITH PASSWORD '$SLACK_APP_POSTGRES_PASSWORD';
  GRANT ALL ON SCHEMA public TO "$SLACK_APP_POSTGRES_USERNAME"
EOSQL

#	GRANT ALL ON SCHEMA public TO "thank-you-slack-bot";
#	CREATE DATABASE thank_you;
#	GRANT ALL ON thank_you TO "thank-you-slack-bot";
