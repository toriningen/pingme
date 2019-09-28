const Telegraf = require('telegraf');
const Telegram = require('telegraf/telegram');
const express = require('express');

const API_TOKEN = process.env.API_TOKEN;
const CHAT_ID = +process.env.CHAT_ID;
const PORT = +process.env.PORT || 8080;

function delay(t) {
    return new Promise((resolve) => {
        setTimeout(resolve, t);
    });
}

async function main() {
    if (!API_TOKEN) {
        console.error("You have no API_TOKEN.\n\nMessage https://t.me/BotFather, create new bot, get API token, pass it via API_TOKEN environment variable.");
        return;
    }

    if (!CHAT_ID) {
        console.warn("WARNING: You have no CHAT_ID, forwarder will be disabled.\n\nMessage your bot with /start, it will tell you your CHAT_ID, or add it into group.\n\n");
    }

    const telegraf = new Telegraf(API_TOKEN, {});
    const telegram = new Telegram(API_TOKEN, {});
    const app = express();
    
    app.use(express.json());
    
    const my = await telegram.getMe();
    
    console.log("Bot info: ", my);
    
    if (CHAT_ID) {
        app.post('/pingme', async (req, res) => {
            for (const message of req.body) {
                while (true) {
                    try {
                        await telegram.sendMessage(
                            CHAT_ID,
                            message,
                            { parse_mode: "HTML" }
                        );
                        break
                    } catch (e) {
                        console.error('Error while trying to send message', e);
                        await delay(1000);
                        continue;
                    }
                }
            }
            
            res.status(200).end();
        });
    }

    // do not respond to any unrecognized requests
    // app.use((req, res, next) => {
    //     res.connection.destroy();
    // });
    
    app.listen(PORT, () => {
        console.log(`listening on ${PORT}`);
    });
    
    telegraf.start((ctx) => {
        ctx.reply(`This chat ID: <code>${ctx.chat.id}</code>`, { parse_mode: "html" });
    });
    
    await telegraf.launch();
}

main().catch((e) => console.error("error", e));
