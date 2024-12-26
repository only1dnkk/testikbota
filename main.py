import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token='7629383884:AAEzg4h2pdUchmdv8-jJkQ6LvfGnZ0-bpec',
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Словарь для хранения статусов пользователей
user_states = {}
# Словарь для хранения количества поклонов
bow_counts = {}

# Целевая группа
TARGET_GROUP_ID = -1001476569128  # Замените на ID группы @addleanchat

@dp.message(Command('chill'))
async def chill_command(message: types.Message):
    # Проверяем, что сообщение из целевой группы
    if message.chat.id != TARGET_GROUP_ID:
        return
        
    user_id = message.from_user.id
    
    # Проверяем, не чиллит ли уже пользователь
    if user_id in user_states and user_states[user_id]['status'] == 'chilling':
        return
        
    user_states[user_id] = {
        'status': 'chilling',
        'start_time': datetime.now()
    }
    await message.reply("Вы начали чиллить! 😎")

@dp.message(Command('tilt'))
async def tilt_command(message: types.Message):
    # Проверяем, что сообщение из целевой группы
    if message.chat.id != TARGET_GROUP_ID:
        return
        
    user_id = message.from_user.id
    
    # Проверяем, не тильтует ли уже пользователь
    if user_id in user_states and user_states[user_id]['status'] == 'tilting':
        return
        
    user_states[user_id] = {
        'status': 'tilting',
        'start_time': datetime.now()
    }
    await message.reply("Вы начали тильтовать! 😡")

@dp.message(Command('поклон'))
async def bow_command(message: types.Message):
    # Проверяем, что сообщение из целевой группы
    if message.chat.id != TARGET_GROUP_ID:
        return

    # Проверяем наличие упоминания пользователя
    if not message.entities or not any(entity.type == 'mention' for entity in message.entities):
        await message.reply("Укажите пользователя через @username")
        return

    # Получаем username пользователя, которому кланяются
    mentioned_username = message.text.split()[1]
    if not mentioned_username.startswith('@'):
        await message.reply("Укажите пользователя через @username")
        return

    # Увеличиваем счетчик поклонов
    if mentioned_username not in bow_counts:
        bow_counts[mentioned_username] = 1
    else:
        bow_counts[mentioned_username] += 1

    await message.reply(f"Вы поклонились {mentioned_username}! 🙇")

@dp.message(Command('status'))
async def status_command(message: types.Message):
    # Проверяем, что сообщение из целевой группы
    if message.chat.id != TARGET_GROUP_ID:
        return
        
    # Проверяем, является ли сообщение ответом на другое сообщение
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.full_name
        mentioned_username = f"@{message.reply_to_message.from_user.username}" if message.reply_to_message.from_user.username else None
    else:
        user_id = message.from_user.id
        username = message.from_user.full_name
        mentioned_username = f"@{message.from_user.username}" if message.from_user.username else None

    status_text = ""
    
    # Проверяем статус пользователя
    if user_id in user_states:
        user_state = user_states[user_id]
        duration = datetime.now() - user_state['start_time']
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        
        if hours > 0:
            time_str = f"{hours} ч. {minutes} мин."
        else:
            time_str = f"{minutes} мин."
            
        if user_state['status'] == 'chilling':
            status_text = f"{username} в чилле уже {time_str} 😎\n"
        elif user_state['status'] == 'tilting':
            status_text = f"{username} в тильте уже {time_str} 😡\n"
    else:
        status_text = f"{username} ничего не делает 😐\n"

    # Добавляем информацию о поклонах
    if mentioned_username and mentioned_username in bow_counts:
        status_text += f"Этому пользователю поклонились {bow_counts[mentioned_username]} раз(а) 🙇"
    elif mentioned_username:
        status_text += "Этому пользователю еще никто не кланялся 🙇"

    await message.reply(status_text)

async def main():
    # Устанавливаем команды бота
    await bot.set_my_commands([
        types.BotCommand(command="chill", description="Начать чиллить"),
        types.BotCommand(command="tilt", description="Начать тильтовать"),
        types.BotCommand(command="status", description="Проверить статус"),
        types.BotCommand(command="poklon", description="Поклониться пользователю")
    ])
    
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    try:
        asyncio.run(main())
    finally:
        # Ensure proper cleanup
        if not bot.session.closed:
            asyncio.run(bot.session.close())
