import time

import telebot

bot = telebot.TeleBot("132:TOKEN")


@bot.message_handler(content_types=["photo"])
def send_text(message):
    try:
        file_name = message.document.file_name
        file_id = message.document.file_name
        file_id_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_id_info.file_path)
        src = file_name
        print(src)
        with open(src, "wb") as new_file:
            new_file.write(downloaded_file)
        bot.send_message(
            message.chat.id,
            "[*] File added:\nFile name - {}".format(
                str(file_name),
            ),
        )
    except Exception as ex:
        bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


while True:
    try:
        print("[*] bot starting..")
        print("[*] bot started!")
        bot.polling(none_stop=True, interval=2)
        break
    except Exception as ex:
        print("[*] error - {}".format(str(ex)))
        print("[*] rebooting..")
        bot.stop_polling()
        time.sleep(15)
        print("[*] restarted!")
