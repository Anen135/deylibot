import pytz
import discord
import datetime

# Токен (лучше брать из переменных окружения в проде)
TOKEN = "MTM4Mjk2NTI5ODY3NTU4NTAzNA.GNhCjg.WSTWRLXnZ_m6EkoTsdERpPX6dPhk6CtPW3Hzlw"

# ID нужных каналов
TARGET_TEXT_CHANNEL_ID = 123456789012345678
TARGET_VC_ID = 1356206346491400282

SOURCE_VC_IDS = [
    1238369263006388245, 1082183176019005501, 1301517898484813896,
    943130959421767707, 977119532009291837, 1000999038784647228,
    1028904893144125500, 1203652885028802600, 1095638837125988392,
    996669365527269386, 1158370586989441115, 1173231115075592323,
    1199920814628294758,
]

# Настройка intents
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

# Для возврата участников
user_original_channels = {}

@client.event
async def on_ready():
    print(f"[READY] Logged in as {client.user}", flush=True)
    await do_daily_task()
    print("[DONE] Задача выполнена, выключаемся...", flush=True)
    await client.close()

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.strip().lower() == "!shutdown":
        await message.channel.send("📦 Завершение: возвращаю участников по местам...")
        await return_users()
        await message.channel.send("✅ Пользователи возвращены. Бот завершает работу.")
        print("[✓] Завершение по команде.")
        await client.close()

async def do_daily_task():
    tz = pytz.timezone('Asia/Almaty')
    now = datetime.datetime.now(tz)
    print(f"[~] Старт задачи: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    for guild in client.guilds:
        target_channel = guild.get_channel(TARGET_VC_ID)
        text_channel = guild.get_channel(TARGET_TEXT_CHANNEL_ID)

        if not target_channel:
            print(f"[!] Целевой голосовой канал не найден: ID={TARGET_VC_ID}")
            continue

        if text_channel:
            try:
                await text_channel.send("🌞 Доброе утро, коллеги! Желаю вам продуктивного дня! 💪")
                print(f"[✔] Утреннее сообщение отправлено в #{text_channel.name}")
            except Exception as e:
                print(f"[✘] Ошибка отправки сообщения: {e}")

        for vc in guild.voice_channels:
            if vc.id not in SOURCE_VC_IDS:
                continue

            for member in vc.members:
                if member.bot or not member.voice:
                    continue
                try:
                    user_original_channels[member.id] = vc.id
                    await member.move_to(target_channel)
                    print(f"[→] {member.display_name} перемещён из {vc.name}")
                except discord.Forbidden:
                    print(f"[✘] Нет прав на перемещение {member.display_name}")
                except Exception as e:
                    print(f"[✘] Ошибка при перемещении {member.display_name}: {e}")

async def return_users():
    for guild in client.guilds:
        for member in guild.members:
            if not member.voice or member.id not in user_original_channels:
                continue

            original_channel_id = user_original_channels.get(member.id)
            original_channel = guild.get_channel(original_channel_id)

            if original_channel:
                try:
                    await member.move_to(original_channel)
                    print(f"[⏪] {member.display_name} возвращён в {original_channel.name}")
                except Exception as e:
                    print(f"[✘] Не удалось вернуть {member.display_name}: {e}")

# Запуск бота
if __name__ == "__main__":
    try:
        print("[LOG] Запуск Discord-клиента...")
        client.run(TOKEN)
    except discord.LoginFailure:
        print("[FATAL] ❌ Неверный токен Discord — проверь переменную TOKEN")
    except Exception as e:
        print(f"[FATAL] ⚠️ Ошибка при запуске бота: {e}")
