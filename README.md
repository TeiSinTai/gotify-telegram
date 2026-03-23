
# Gotify Telegram Bot

A Gotify client that broadcast notifications to a specific Telegram Bot (user driven) thats talk to a specific Telegram user.

## Features

- Broadcast Gotify notifications to Telegram
- Telegram Bot for control Gotify Server (user driven)
- Posibillity to send notifications to Gotify
- Receive notifications of multi gotify servers on same Telegram Bot

## Requirements

- Gotify deployment
- Gotify Client Token
- Telegram Bot Token [gen with @BotFather]
- Telegram Chat ID [for receive notifications]

## Environment Variables

To run this project, you will need to add the following environment variables. One way to setup this variables its using `docker-compose` for deployment.

- `GOTIFY_URL`
- `GOTIFY_PORT`
- `GOTIFY_CLIENT_TOKEN`
- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`

## Building
```
docker build . -t gotify-telegram

```

## compose example
```YAML
version: '3.7'

services:

  gotify-telegram:
    image: gotify-telegram
    container_name: gotify-telegram
    restart: unless-stopped
    environment:
      - GOTIFY_URL=A.B.C.D
      - GOTIFY_PORT=8124
      - GOTIFY_CLIENT_TOKEN=ZZZZZZZZZZZZZZZZ
      - TELEGRAM_CHAT_ID=-YYYYYYYYYYYYYYYY
      - TELEGRAM_TOKEN=NNNNNN:XXXXXXXXXXXXXXXXXXXXXX
```