import os
import pytz
import discord
import datetime
import asyncio

TOKEN = os.environ["DISCORD_TOKEN"]

TARGET_TEXT_CHANNEL_ID = 123456789012345678
TARGET_VC_ID = 1356206346491400282

SOURCE_VC_IDS = [
    1238369263006388245,
    1082183176019005501,
    1301517898484813896,
    943130959421767707,
    977119532009291837,
    1000999038784647228,
    1028904893144125500,
    1203652885028802600,
    1095638837125988392,
    996669365527269386,
    1158370586989441115,
    1173231115075592323,
    1199920814628294758,
]

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"[+] Бот вошёл как {client.user}")
    await do_daily_task()
    print("[✓] Задача завершена. Завершаем процесс...")
    await client.close()


async def do_daily_task():
    tz = pytz.timezone('Asia/Almaty')
    now = datetime.datetime.now(tz)
    print(f"[~] Выполнение задачи: {now.strftime('%Y-%m-%d %H:%M')}")

    for guild in client.guilds:
        target_channel = guild.get_channel(TARGET_VC_ID)
        text_channel = guild.get_channel(TARGET_TEXT_CHANNEL_ID)

        if not target_channel:
            print(f"[!] Голосовой канал не найден: {TARGET_VC_ID}")
            continue

        if text_channel:
            try:
                await text_channel.send("🌞 Доброе утро, коллеги! Желаю вам продуктивного дня! 💪")
                print(f"[✔] Сообщение отправлено в {text_channel.name}")
            except Exception as e:
                print(f"[✘] Не удалось отправить сообщение: {e}")

        moved_users = set()
        for voice_channel in guild.voice_channels:
            if voice_channel.id not in SOURCE_VC_IDS:
                continue
            for member in voice_channel.members:
                if member not in moved_users and member.voice:
                    try:
                        await member.move_to(target_channel)
                        moved_users.add(member)
                        print(f"[✔] Перемещён: {member.display_name}")
                    except discord.Forbidden:
                        print(f"[✘] Нет прав: {member.display_name}")
                    except Exception as e:
                        print(f"[✘] Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(client.start(TOKEN))
