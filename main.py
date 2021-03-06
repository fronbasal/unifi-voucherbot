import telegram
import os
import logging

from telegram import TelegramError
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from unifipy import Unifi


def _(s): return os.environ.get(s)


class MissingTokenError(Exception):
    pass


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Welcome, I'm the Unifi Voucherbot for the Steinbart-Gymnasium." +
                                  "\n You can find my source code here: https://github.com/fronbasal/unifi-voucherbot." +
                                  "\n You may generate a classroom voucher by typing /generate.")


def generate(update, context):
    logging.log(logging.INFO, "User @" + update.effective_user.username + " generated a voucher.")
    try:
        vouchers = unifi_api.generate_voucher(_("UNIFI_VOUCHER_EXPIRE"), _("UNIFI_VOUCHER_USAGES"))
    except Exception:
        logging.log(logging.ERROR, "Failed to generate voucher!")
        return

    if vouchers is not None:
        for voucher in vouchers:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text="Congratulations! Your voucher has been generated.\n" +
                                          "Please use the voucher " + voucher['code'] + " to log in to the WiFi.\n" +
                                          "The voucher is valid for " +
                                          _("UNIFI_VOUCHER_EXPIRE") + " minutes and can be used "
                                          + _("UNIFI_VOUCHER_USAGES") + " times.")
    else:
        raise TelegramError


def unknown(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Unknown command. Type /generate to get a new voucher.")


if __name__ == '__main__':
    assert any(x in os.environ for x in
               ("TELEGRAM_TOKEN", "UNIFI_USERNAME", "UNIFI_PASSWORD", "UNIFI_URL")), \
        MissingTokenError("Missing required env variable")

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    token = _("TELEGRAM_TOKEN")
    logging.log(logging.INFO, f"Using Telegram token " + token)

    unifi_api = Unifi(_("UNIFI_USERNAME"), _("UNIFI_PASSWORD"), _("UNIFI_URL"),
                      _("UNIFI_SITE"))
    logging.log(logging.INFO, "Connected to Unifi API")

    bot = telegram.Bot(token)

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    logging.log(logging.INFO, f"Logged in as " + bot.username)

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    generate_handler = CommandHandler("generate", generate)
    dispatcher.add_handler(generate_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    logging.log(logging.INFO, "Bot started")
