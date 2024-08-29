import asyncio
import json
import logging
import os
from os import getenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import aiohttp

load_dotenv(dotenv_path=".env")

BOT_TOKEN = getenv("BOT_TOKEN")
ITMO_TOKEN = getenv("ITMO_TOKEN")
ADMIN_ID = int(getenv("ADMIN_ID"))

dp = Dispatcher()

subscribed_chats = {}
subjects_data = None
SUBSCRIBED_CHATS_FILE = "subscribed_chats.json"


def load_subscribed_chats():
    global subscribed_chats
    try:
        with open(SUBSCRIBED_CHATS_FILE, "r") as f:
            subscribed_chats = json.load(f)
    except FileNotFoundError:
        subscribed_chats = {}


def save_subscribed_chats():
    with open(SUBSCRIBED_CHATS_FILE, "w") as f:
        json.dump(subscribed_chats, f)


async def get_itmo_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru",
        "Authorization": f"Bearer {ITMO_TOKEN}",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://my.itmo.ru/election",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://my.itmo.ru/api/election/students/ordered_flow_chains",
            headers=headers,
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                logging.error(f"Ошибка при получении данных: {response.status}")
                return None


async def get_itmo_limits():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru",
        "Authorization": f"Bearer {ITMO_TOKEN}",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://my.itmo.ru/election",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://my.itmo.ru/api/election/students/limits/flows", headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                logging.error(f"Ошибка при получении лимитов: {response.status}")
                return None


def extract_structure(data):
    structure = []
    if data is None or "result" not in data:
        return structure

    for discipline in data["result"]:
        discipline_item = {
            "id": discipline["disciplineId"],
            "name": discipline["disciplineName"],
            "flows": [],
        }
        for flow in discipline["flows"]:
            flow_item = {"id": flow["id"], "name": flow["name"], "variants": []}
            for variant in flow["variants"]:
                variant_item = {
                    "id": variant["id"],
                    "name": variant["name"],
                    "sub_variants": [],
                }
                if "variants" in variant:
                    for sub_variant in variant["variants"]:
                        sub_variant_item = {
                            "id": sub_variant["id"],
                            "name": sub_variant["name"],
                        }
                        variant_item["sub_variants"].append(sub_variant_item)
                flow_item["variants"].append(variant_item)
            discipline_item["flows"].append(flow_item)
        structure.append(discipline_item)

    return structure


def format_item_data(item, limits):
    limit_data = limits.get("result", {}).get(str(item["id"]), {})
    return (
        f"{item['name']}:\n"
        f"Макс. количество студентов: {limit_data.get('limitMax', 'Не указано')}\n"
        f"Занято мест: {limit_data.get('occupied', 'Не указано')}\n"
        f"Свободно мест: {limit_data.get('free', 'Не указано')}\n"
    )


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! "
        f"Используй /subscribe для подписки на обновления или /unsubscribe для отписки. "
        f"Используй /get_data для получения данных о подписанных вариантах."
    )


@dp.message(Command("subscribe"))
async def subscribe_handler(message: Message) -> None:
    chat_id = str(message.chat.id)
    if chat_id not in subscribed_chats:
        subscribed_chats[chat_id] = []

    structure = extract_structure(subjects_data)
    keyboard = InlineKeyboardBuilder()
    for discipline in structure:
        keyboard.button(
            text=discipline["name"], callback_data=f"discipline_{discipline['id']}"
        )
    keyboard.adjust(2)

    await message.answer("Выберите дисциплину:", reply_markup=keyboard.as_markup())


@dp.callback_query(F.data.startswith("discipline_"))
async def discipline_callback(callback: CallbackQuery):
    discipline_id = int(callback.data.split("_")[1])
    structure = extract_structure(subjects_data)
    discipline = next((d for d in structure if d["id"] == discipline_id), None)

    if discipline:
        keyboard = InlineKeyboardBuilder()
        for flow in discipline["flows"]:
            keyboard.button(text=flow["name"], callback_data=f"flow_{flow['id']}")
        keyboard.adjust(2)
        await callback.message.edit_text(
            f"Выберите поток для {discipline['name']}:",
            reply_markup=keyboard.as_markup(),
        )
    else:
        await callback.answer("Дисциплина не найдена")


@dp.callback_query(F.data.startswith("flow_"))
async def flow_callback(callback: CallbackQuery):
    flow_id = int(callback.data.split("_")[1])
    structure = extract_structure(subjects_data)
    flow = next((f for d in structure for f in d["flows"] if f["id"] == flow_id), None)

    if flow:
        keyboard = InlineKeyboardBuilder()
        for variant in flow["variants"]:
            keyboard.button(
                text=variant["name"], callback_data=f"variant_{variant['id']}"
            )
        keyboard.adjust(2)
        await callback.message.edit_text(
            f"Выберите вариант для {flow['name']}:", reply_markup=keyboard.as_markup()
        )
    else:
        await callback.answer("Поток не найден")


@dp.callback_query(F.data.startswith("variant_"))
async def variant_callback(callback: CallbackQuery):
    variant_id = int(callback.data.split("_")[1])
    structure = extract_structure(subjects_data)
    variant = next(
        (
            v
            for d in structure
            for f in d["flows"]
            for v in f["variants"]
            if v["id"] == variant_id
        ),
        None,
    )

    if variant:
        if variant["sub_variants"]:
            keyboard = InlineKeyboardBuilder()
            for sub_variant in variant["sub_variants"]:
                keyboard.button(
                    text=sub_variant["name"],
                    callback_data=f"subscribe_{sub_variant['id']}",
                )
            keyboard.adjust(2)
            await callback.message.edit_text(
                f"Выберите подвариант для {variant['name']}:",
                reply_markup=keyboard.as_markup(),
            )
        else:
            chat_id = str(callback.message.chat.id)
            if variant_id not in subscribed_chats[chat_id]:
                subscribed_chats[chat_id].append(variant_id)
                save_subscribed_chats()
                await callback.answer(f"Вы подписались на вариант {variant['name']}")
            else:
                await callback.answer("Вы уже подписаны на этот вариант")
    else:
        await callback.answer("Вариант не найден")


@dp.callback_query(F.data.startswith("subscribe_"))
async def subscribe_callback(callback: CallbackQuery):
    sub_variant_id = int(callback.data.split("_")[1])
    chat_id = str(callback.message.chat.id)

    if sub_variant_id not in subscribed_chats[chat_id]:
        subscribed_chats[chat_id].append(sub_variant_id)
        save_subscribed_chats()
        await callback.answer(f"Вы подписались на подвариант {sub_variant_id}")
    else:
        await callback.answer("Вы уже подписаны на этот подвариант")


@dp.message(Command("unsubscribe"))
async def unsubscribe_handler(message: Message) -> None:
    chat_id = str(message.chat.id)
    if chat_id in subscribed_chats and subscribed_chats[chat_id]:
        keyboard = InlineKeyboardBuilder()
        structure = extract_structure(subjects_data)
        for item_id in subscribed_chats[chat_id]:
            item = next(
                (
                    v
                    for d in structure
                    for f in d["flows"]
                    for v in f["variants"]
                    for sv in v["sub_variants"]
                    if sv["id"] == item_id
                ),
                None,
            )
            if item:
                keyboard.button(
                    text=item["name"], callback_data=f"unsubscribe_{item['id']}"
                )
        keyboard.adjust(2)
        await message.answer(
            "Выберите варианты для отписки:", reply_markup=keyboard.as_markup()
        )
    else:
        await message.answer("Вы не подписаны ни на один вариант.")


@dp.callback_query(F.data.startswith("unsubscribe_"))
async def unsubscribe_callback(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    chat_id = str(callback.message.chat.id)

    if item_id in subscribed_chats[chat_id]:
        subscribed_chats[chat_id].remove(item_id)
        save_subscribed_chats()
        await callback.answer(f"Вы отписались от варианта {item_id}")
    else:
        await callback.answer("Вы не были подписаны на этот вариант")


@dp.message(Command("get_data"))
async def get_data_handler(message: Message):
    global subjects_data

    chat_id = str(message.chat.id)
    if chat_id not in subscribed_chats or not subscribed_chats[chat_id]:
        await message.answer(
            "Вы еще не выбрали ни одного варианта. Используйте /select для выбора."
        )
        return

    limits_data = await get_itmo_limits()
    response = "Информация о выбранных вариантах:\n\n"

    if not subjects_data:
        subjects_data = await get_itmo_data()

    for item_id in subscribed_chats[chat_id]:
        item = next(
            (
                v
                for d in subjects_data["result"]
                for f in d["flows"]
                for v in f["variants"]
                if v["id"] == item_id
            ),
            None,
        )

        if item:
            subject = next(
                s
                for s in subjects_data["result"]
                if any(
                    f
                    for f in s["flows"]
                    if any(v for v in f["variants"] if v["id"] == item_id)
                )
            )
            flow = next(
                f
                for f in subject["flows"]
                if any(v for v in f["variants"] if v["id"] == item_id)
            )

            places_info = (
                limits_data["result"].get(str(flow["id"]), {})
                if limits_data and limits_data.get("result")
                else {}
            )

            response += f"Предмет: {subject['disciplineName']}\n"
            response += f"Поток: {flow['name']}\n"
            response += f"Вариант: {item['name']}\n"
            response += f"Преподаватель: {', '.join(item['teachers'])}\n"
            response += (
                f"Максимум студентов: {places_info.get('limitMax', 'Нет данных')}\n"
            )
            response += f"Занято мест: {places_info.get('occupied', 'Нет данных')}\n"
            response += f"Свободно мест: {places_info.get('free', 'Нет данных')}\n"
            response += f"Доступен: {'Да' if item['available'] else 'Нет'}\n\n"

    await message.answer(response)


@dp.message(Command("update_token"))
async def update_token_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    new_token = (
        message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    )

    if not new_token:
        await message.answer("Пожалуйста, укажите новый токен после команды.")
        return

    global ITMO_TOKEN
    ITMO_TOKEN = new_token

    if not new_token:
        await message.answer("Пожалуйста, укажите новый токен после команды.")
        return

    if os.path.exists(".env"):
        with open(".env", "r") as file:
            lines = file.readlines()
        with open(".env", "w") as file:
            for line in lines:
                if line.startswith("ITMO_TOKEN="):
                    file.write(f"ITMO_TOKEN={new_token}\n")
                else:
                    file.write(line)

    await message.answer("Токен успешно обновлен.")


async def periodic_updates(bot: Bot):
    global subjects_data

    while True:
        limits_data = await get_itmo_limits()
        if not limits_data:
            logging.error("Ошибка при получении лимитов")
            await asyncio.sleep(300)
            continue
        for chat_id, subscribed_items in subscribed_chats.items():
            response = "Обновленная информация о выбранных вариантах:\n\n"

            if not subjects_data:
                subjects_data = await get_itmo_data()

            for item_id in subscribed_items:
                item = next(
                    (
                        v
                        for d in subjects_data["result"]
                        for f in d["flows"]
                        for v in f["variants"]
                        if v["id"] == item_id
                    ),
                    None,
                )

                if item:
                    subject = next(
                        s
                        for s in subjects_data["result"]
                        if any(
                            f
                            for f in s["flows"]
                            if any(v for v in f["variants"] if v["id"] == item_id)
                        )
                    )
                    flow = next(
                        f
                        for f in subject["flows"]
                        if any(v for v in f["variants"] if v["id"] == item_id)
                    )

                    places_info = (
                        limits_data["result"].get(str(flow["id"]), {})
                        if limits_data and limits_data.get("result")
                        else {}
                    )

                    response += f"Предмет: {subject['disciplineName']}\n"
                    response += f"Поток: {flow['name']}\n"
                    response += f"Вариант: {item['name']}\n"
                    response += f"Преподаватель: {', '.join(item['teachers'])}\n"
                    response += f"Максимум студентов: {places_info.get('limitMax', 'Нет данных')}\n"
                    response += (
                        f"Занято мест: {places_info.get('occupied', 'Нет данных')}\n"
                    )
                    response += (
                        f"Свободно мест: {places_info.get('free', 'Нет данных')}\n"
                    )
                    response += f"Доступен: {'Да' if item['available'] else 'Нет'}\n\n"

            await bot.send_message(
                chat_id=int(chat_id), text=response, disable_notification=True
            )

        await asyncio.sleep(300)


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    load_subscribed_chats()
    global subjects_data
    subjects_data = await get_itmo_data()
    asyncio.create_task(periodic_updates(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
