import os
import pytz
import discord
from discord.ext import commands, tasks
import datetime
import asyncio
import random

# Токен бота
TOKEN = os.environ["DISCORD_TOKEN"]

TARGET_TEXT_CHANNEL_ID = 123456789012345678  #Дейлик
TARGET_VC_ID = 1356206346491400282   #Дейлик

SOURCE_VC_IDS = [
    1238369263006388245,  #Semey Room
    1082183176019005501,  #Damir-Bauka
    1301517898484813896,  #Dauytbek
    943130959421767707,  #Aidos Room
    977119532009291837,  #Valikhan Room
    1000999038784647228,  #Baurzhan Room
    1028904893144125500,  #обучение
    1203652885028802600,  #Ali-Nurasyl
    1095638837125988392,  #Dias Room
    996669365527269386,  #Владимир Room
    1158370586989441115,  #gosagro
    1173231115075592323,  #Аналитика
    1199920814628294758,  #Последний канал
]

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
  if bot.user is None or bot.user.id is None:
    print("[!] Не удалось получить информацию о боте")
    return
  print(f"[+] Бот успешно запущен как {bot.user} ({bot.user.id})")
  if not hasattr(bot, "background_task_started"):
    bot.background_task_started = True
    asyncio.create_task(wait_until_11())


@bot.command(name='moveall')
async def move_all(ctx):
  guild = ctx.guild
  target_channel = guild.get_channel(TARGET_VC_ID)

  if not target_channel:
    await ctx.send(f"[!] Целевой голосовой канал не найден.")
    return

  moved_users = set()
  for voice_channel in guild.voice_channels:
    if voice_channel.id not in SOURCE_VC_IDS:
      continue
    for member in voice_channel.members:
      if member not in moved_users and member.voice:
        try:
          await member.move_to(target_channel)
          moved_users.add(member)
        except discord.Forbidden:
          await ctx.send(f"[✘] Нет прав для перемещения {member.display_name}")
        except Exception as e:
          await ctx.send(f"[✘] Ошибка с {member.display_name}: {e}")

  await ctx.send(
      f"[✔] Перемещено {len(moved_users)} участников в {target_channel.name}")
  await ctx.send("🌞 Доброе утро, коллеги! Желаю вам продуктивного дня! 💪")


async def wait_until_11():
  tz = pytz.timezone('Asia/Almaty')
  while True:
    now = datetime.datetime.now(tz)
    target_time = now.replace(hour=11, minute=0, second=0, microsecond=0)
    if now >= target_time:
      target_time += datetime.timedelta(days=1)
    while target_time.weekday() >= 5:
      target_time += datetime.timedelta(days=1)

    wait_seconds = (target_time - now).total_seconds()
    print(
        f"[~] Спим до {target_time.strftime('%Y-%m-%d %H:%M:%S')} (~{wait_seconds/60:.1f} минут)"
    )
    await asyncio.sleep(wait_seconds)
    await do_daily_task()


async def do_daily_task():
  tz = pytz.timezone('Asia/Almaty')
  now = datetime.datetime.now(tz)

  print(f"[~] Выполнение задачи: {now.strftime('%Y-%m-%d %H:%M')}")

  for guild in bot.guilds:
    target_channel = guild.get_channel(TARGET_VC_ID)
    text_channel = guild.get_channel(TARGET_TEXT_CHANNEL_ID)

    if not target_channel:
      print(f"[!] Голосовой канал не найден: {TARGET_VC_ID}")
      continue

    if text_channel:
      try:
        await text_channel.send(
            "🌞 Доброе утро, коллеги! Желаю вам продуктивного дня! 💪")
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


# Запуск бота
if __name__ == '__main__':
  try:
    bot.run(TOKEN)
  except Exception as e:
    print(f"[FATAL] Не удалось запустить бота: {e}")