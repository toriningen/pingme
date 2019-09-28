# Simple telegram forwarder

## Quickstart

Message [@BotFather](https://t.me/BotFather), create a new bot, and it will tell you an API token. Record it.

First, start the bot like this (don't forget to replace API_TOKEN with what you've got from BotFather):

    $ docker run --rm -it --name "pingme" \
        --init \
        -p 8080:8080 \
        -e "API_TOKEN=123456789:AbCdfGhIJKlmNoQQRsTUVwxyZ" \
        toriningen/pingme

Now message your bot with `/start` in personal chat, or add it to group and message `/start@your_bot` (replacing the username with proper one). Your bot will tell you chat ID. Record it.

Now kill your bot instance with Ctrl+C and start it like this:

    $ docker run -d --name "pingme" \
        --init \
        -p 8080:8080 \
        -e "API_TOKEN=123456789:AbCdfGhIJKlmNoQQRsTUVwxyZ" \
        -e "CHAT_ID=9191919191" \
        toriningen/pingme

Don't forget to replace `CHAT_ID` with the identifier you got from bot. Now you're done.

## Running without Docker

Install Node.js, clone this repo, run:

    $ cd app
    $ npm i

This will install runtime dependencies. To run forwarder itself:

    $ export PORT=8080
    $ export API_TOKEN=123456789:AbCdfGhIJKlmNoQQRsTUVwxyZ
    $ export CHAT_ID=12345678
    $ node index.js

Workflow is the same as with Docker.

## Sending messages with Python

Import `Reporter` class from `reporter.py` somehow. Then use like this:

    reporter = Reporter("your-host:8080") # where is pingme daemon running?
    
    @reporter
    def train_model(params):
        print("training...")
        
        loss = 1000
        
        for epoch in range(100):
            time.sleep(0.1)
            loss /= 2
            if epoch % 10 == 9:
                # send updates on the go if you want
                reporter.send(f"<b>Still training!</b>\nloss = <code>{loss}</code>")
        
        return { "loss": 0.9 } # anything

## Sending messages with curl

Send messages via HTTP like this:

    $ curl http://your-host:8080/pingme \
        -H 'Content-Type: application/json' \
        --data '["<b>This is test!</b>\nlol, it works"]'

`Content-Type` header is mandatory.
