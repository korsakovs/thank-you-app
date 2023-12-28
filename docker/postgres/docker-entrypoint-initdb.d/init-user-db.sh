#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER "thank-you-slack-bot" WITH PASSWORD 'thank-you-slack-bot';
	GRANT ALL ON SCHEMA public TO "thank-you-slack-bot";
EOSQL

#	CREATE DATABASE thank_you;
#	GRANT ALL ON thank_you TO "thank-you-slack-bot";
