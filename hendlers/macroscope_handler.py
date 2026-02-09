from aiogram import types, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
import requests

router = Router()

def get_keyboard():
    buttons = [
        [types.InlineKeyboardButton(text="Все сервера", callback_data="cam_all")],
        [
            types.InlineKeyboardButton(text="Сервера с проблемой", callback_data="cam_err"),
            types.InlineKeyboardButton(text="Здоровые сервера", callback_data="cam_ok"),
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

@router.message(Command("camserver"))
@router.message(CommandStart(
    deep_link=True, magic=F.args == "camserver"
))
async def cmd_start_server(message: types.Message):
    await cmd_camserver(message)

@router.message(Command("camserver"))
async def cmd_camserver(message: types.Message):
    await message.answer("Что вы хотите посмотреть?", reply_markup=get_keyboard())

@router.callback_query(F.data.startswith("cam_"))
async def callbacks_cam(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    try:
        response = requests.get('http://10.2.1.131:8000/api/servers', timeout=25)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        await callback.answer(f"❌ Ошибка при запросе к серверу: {e}")
        return
    except ValueError as e:
        await callback.answer(f"❌ Ошибка при разборе JSON: {e}")
        return

    if not data.get('servers'):
        await callback.answer("ℹ️ Нет данных о серверах.")
        return

    await callback.answer()

    total_servers = 0
    sent_servers = 0

    for server in data['servers']:
        server_name = server.get('name', 'Неизвестный сервер')
        server_status = server.get('status', "Неизвестный статус")

        total_cameras = server.get('cameras_count', 0)
        active_cameras = server.get('cameras_active', 0)
        error_cameras = server.get('cameras_errors', 0)

        if error_cameras == 0 and total_cameras > 0:
            status_emoji = "✅"
        elif error_cameras > 0 and active_cameras > 0:
            status_emoji = "⚠️"
        else:
            status_emoji = "❌"

        if server_status == "error":
            stat = "❌❌❌НЕ РАБОТАЕТ❌❌❌"
        elif server_status == "ok" or server_name == "Ok":
            stat = "✅РАБОТАЕТ✅"

        server_info = (
            f"{status_emoji} <b>Сервер: {server_name}</b>\n"
            f"<b>Состояние: {stat}</b>\n\n"
            f"🖥️ <b>Статистика камер:</b>\n"
            f"📊 Всего камер: <code>{total_cameras}</code>\n"
            f"🟢 Работает: <code>{active_cameras}</code>\n"
            f"🔴 Не работает: <code>{error_cameras}</code>\n"
        )

        if total_cameras > 0:
            success_rate = (active_cameras / total_cameras) * 100
            server_info += f"📈 Работоспособность: <code>{success_rate:.1f}%</code>\n"

        should_send = False
        if action == "err":
            if server_status == "error" or error_cameras > 0:
                should_send = True
        elif action == "ok":
            if server_status == "ok" and error_cameras == 0:
                should_send = True
        elif action == "all":
            should_send = True

        if should_send:
            total_servers += 1
            try:
                await callback.message.answer(server_info, parse_mode=ParseMode.HTML)
                sent_servers += 1
            except Exception as e:
                await callback.message.answer(f"❌ Ошибка при отправке информации о сервере {server_name}: {e}")

    if sent_servers == 0:
        if action == "err":
            await callback.message.answer("✅ Нет серверов с проблемами")
        elif action == "ok":
            await callback.message.answer("ℹ️ Нет здоровых серверов")
        else:
            await callback.message.answer("ℹ️ Нет данных о серверах")
    else:
        if action == "err":
            await callback.message.answer(
                f"📊 <b>Итого:</b> Показано {sent_servers} серверов с проблемами из {len(data['servers'])}")
        elif action == "ok":
            await callback.message.answer(
                f"📊 <b>Итого:</b>  {sent_servers} / {len(data['servers'])} работают без каких либо ошибок")
        elif action == "all":
            await callback.message.answer(f"📊 <b>Итого:</b> Показано {sent_servers} серверов")

@router.message(Command("cameras"))
async def cmd_cameras(message: types.Message):
    try:
        response = requests.get('http://10.2.1.131:8000/api/servers', timeout=25)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        await message.answer(f"❌ Ошибка при запросе к серверу: {e}")
        return
    except ValueError as e:
        await message.answer(f"❌ Ошибка при разборе JSON: {e}")
        return
    args = message.text.split(maxsplit=1)
    # Проверяем, есть ли серверы в данных
    if not data.get('servers'):
        await message.answer("ℹ️ Нет данных о серверах.")
        return

    # Отправляем статистику для каждого сервера отдельным сообщением
    for server in data['servers']:
        # Создаем понятное имя сервера (если доступно)
        server_name = server.get('name', 'Неизвестный сервер')
        server_status = server.get('status', "Неизвестный статус")
        # Формируем статистику
        total_cameras = server.get('cameras_count', 0)
        active_cameras = server.get('cameras_active', 0)
        error_cameras = server.get('cameras_errors', 0)

        # Определяем статус сервера для эмодзи
        if error_cameras == 0 and total_cameras > 0:
            status_emoji = "✅"
        elif error_cameras > 0 and active_cameras > 0:
            status_emoji = "⚠️"
        else:
            status_emoji = "❌"

        if server_status == "error":
            stat = "❌❌❌НЕ РАБОТАЕТ❌❌❌"
        elif server_status == "ok" or server_name == "Ok":
            stat = "✅РАБОТАЕТ✅"
        # Формируем сообщение с красивым форматированием
        server_info = (
            f"{status_emoji} <b>Сервер: {server_name}</b>\n"
            f"<b>Состояние: {stat}</b>\n\n"
            f"🖥️ <b>Статистика камер:</b>\n"
            f"📊 Всего камер: <code>{total_cameras}</code>\n"
            f"🟢 Работает: <code>{active_cameras}</code>\n"
            f"🔴 Не работает: <code>{error_cameras}</code>\n"
        )

        # Добавляем процент работающих камер, если есть камеры
        if total_cameras > 0:
            success_rate = (active_cameras / total_cameras) * 100
            server_info += f"📈 Работоспособность: <code>{success_rate:.1f}%</code>\n"

        # Добавляем разделитель между сообщениями
        if server != data['servers'][-1]:
            server_info += "\n" + "─" * 30 + "\n"

        if len(args) > 1 and args[1] == "err":
            if server_status == "error" or error_cameras > 0:
                await message.answer(server_info, parse_mode=ParseMode.HTML)
            else:
                continue
        elif len(args) > 1 and args[1] == "ok":
            if server_status == "ok" and error_cameras == 0:
                await message.answer(server_info, parse_mode=ParseMode.HTML)
            else:
                continue
        else:
            await message.answer(server_info, parse_mode=ParseMode.HTML)

