from aiogram import types, F, html, Router
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import hide_link
from pathlib import Path
import json

router = Router()

current_dir = Path(__file__).parent
file_path = current_dir / "commands_info.json"

with open(file_path, "r", encoding="utf-8") as f:
    commands_info = json.load(f)

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}, программа пока на этапе разработке!")

@router.message(F.text, Command('help'))
async def cmd_help(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        commands = args[1].lstrip('/')
        if commands in commands_info:
            detailed = commands_info[commands].get('detailed', "Нет подробного описания")
            await message.answer(f"Информация по команде /{commands}:\n{detailed}")
        else:
            await message.answer(f"Команда /{commands} не найдена.")
    else:
        help_text = "Доступные команды:\n"
        for cmd, info in commands_info.items():
            help_text += f"/{cmd} - {info['brief']}\n"
        help_text += "Используйте <b><u>/help &lt;command&gt;</u></b> для подробной информации по команде"
        await message.answer(help_text)

@router.message(Command('hide_link'))
async def cmd_hide_link(message: types.Message):
    await message.answer(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Документация Telegram: *существует*\n"
        f"Пользователи: *не читают документацию*\n"
        f"Груша:"
    )

@router.message(F.text)
async def extract_data(message: types.Message):
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "code": "<N/A>"
    }
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            data[item.type] = item.extract_from(message.text)
    await message.reply(
        f"Вот что я нашёл:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Пароль: {html.quote(data['code'])}\n"
    )