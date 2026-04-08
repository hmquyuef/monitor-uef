const TelegramBot = require('node-telegram-bot-api');
const sequelize = require('../config/database');

let bot = null;
let lastToken = null;

async function getBot() {
  const [results] = await sequelize.query("SELECT value FROM system_settings WHERE key = 'telegram_bot_token'");
  const token = results.length > 0 ? results[0].value : null;

  if (!token) return null;

  if (token !== lastToken) {
    bot = new TelegramBot(token, { polling: false });
    lastToken = token;
  }
  return bot;
}

exports.sendAlert = async (message) => {
  try {
    const currentBot = await getBot();
    const [idResults] = await sequelize.query("SELECT value FROM system_settings WHERE key = 'telegram_chat_id'");
    const chatId = idResults.length > 0 ? idResults[0].value : null;

    if (!currentBot || !chatId) {
      console.warn('Telegram Bot or Chat ID not configured in DB.');
      return;
    }

    await currentBot.sendMessage(chatId, `🚨 *MONITOR ALERT*\n\n${message}`, { parse_mode: 'Markdown' });
  } catch (error) {
    console.error('Telegram notification error:', error.message);
  }
};
