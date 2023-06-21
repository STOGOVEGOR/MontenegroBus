# use the https://uptimerobot.com/dashboard#mainDashboard for keep flask server alive
import os
from background import keep_alive
import pip

pip.main(['install', 'pytelegrambotapi'])
import telebot
import time
import pytz
from datetime import date, timedelta, datetime, time, timezone
from replit import db

API_KEY = os.environ['MBUS_BOT_API_KEY']
bot = telebot.TeleBot(API_KEY)
bot_enabled = 1
delay = 10

# [1,2] - 1 to HDL (Igalo), 2 to ferry (or Meljino)
BUSBASE = {
  'Bus1': {
    'Kamenari': [0, 'end'],
    'Bijela': [5,44],
    'Baosici': [15,34],
    'Djenovici': [18,31],
    'Kumbor': [23,26],
    'Zelenika': [26,23],
    'Meljine': [28,20],
    'Savina': [29,15],
    'Centar': [30,12],
    'Semafor': [32,10],
    'IgaloPochta': [35,7],
    'IgaloInstitut': [38,3],
    'HDLVOLI': ['end',0]
  },
  'Bus2':{
    'Meljine': [20,'end'],
    'Savina': [22,15],
    'Centar': [23,12],
    'Semafor': [25,10],
    'IgaloPochta': [28,7],
    'IgaloInstitut': [31,3],
    'HDLVOLI': ['end',0]
  }
}

BUS1_IGALO = [530, 600, 630, 700, 730, 800, 830, 900, 930, 1000, 1030, 1100, 1130, 1200, 1230, 1300, 1330, 1400, 1430, 1500, 1530, 1600, 1630, 1700, 1730, 1800, 1830, 1900, 1930, 2000, 2030, 2100, 2130, 2200, 2300, 2400, 530, 600, 630, 700, 730]
BUS1_IGALO_SUN = [600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 530, 600, 630, 700, 730]
BUS1_KAMEN = [520, 550, 620, 650, 720, 750, 820, 850, 920, 950, 1020, 1050, 1120, 1150, 1220, 1250, 1320, 1350, 1420, 1450, 1520, 1550, 1620, 1650, 1720, 1750, 1820, 1850, 1920, 1950, 2020, 2050, 2120, 2150, 2220, 2250, 2350, 2450, 520, 550, 620, 650, 720]
BUS1_KAMEN_SUN = [550, 650, 750, 850, 950, 1050, 1150, 1250, 1350, 1450, 1550, 1650, 1750, 1850, 1950, 2050, 2150, 2250, 2350, 2450, 550, 650, 750, 850, 950]
BUS2_CIRCLE = [605, 645, 725, 805, 845, 925, 1005, 1045, 1125, 1205, 1245, 1325, 1405, 1445, 1525, 1605, 1645, 1725, 1805, 1845, 1925, 2005, 2045, 605, 645, 725, 805, 845]

# ======== CALC SECTION ==========
def get_current_time() -> datetime:
    delta = timedelta(hours=2, minutes=0)
    and_now = datetime.now(timezone.utc) + delta
    return and_now

# unaware = datetime.datetime(2011, 8, 15, 8, 15, 12, 0)
# aware = datetime.datetime(2011, 8, 15, 8, 15, 12, 0, pytz.UTC)

# now_aware = pytz.utc.localize(unaware)
# assert aware == now_aware


def when_next(bus_stop, bus_num, direction):
    cur_time = get_current_time()
    cur_hour = int(cur_time.strftime("%H")+'00')
    if cur_hour == 0:
      cur_hour = 2400
    cur_minute = cur_time.strftime("%M")   
    day_of_week = cur_time.weekday()
    arrive_on_stop = []
    if bus_stop in BUSBASE[bus_num]:
        correction = BUSBASE[bus_num][bus_stop]
        if direction == 'Igalo':
            correction = correction[0]
            if correction == 'end':
                arrive_on_stop.append('вы на конечной остановке.')
                return arrive_on_stop
        if direction == 'Ferry':
            correction = correction[1]
            if correction == 'end':
                arrive_on_stop.append('вы на конечной остановке.')
                return arrive_on_stop
    else:
        return False

    # if bus_num == 'Bus2' and day_of_week == 6:
    #     print('no bus today')
    if bus_num == 'Bus2':
        BUSSCHEDULE = BUS2_CIRCLE
    if bus_num == 'Bus1':
        if direction == 'Ferry':
            if day_of_week != 6:
                BUSSCHEDULE = BUS1_IGALO
            else:
                BUSSCHEDULE = BUS1_IGALO_SUN
        if direction == 'Igalo':
            if day_of_week != 6:
                BUSSCHEDULE = BUS1_KAMEN
            else:
                BUSSCHEDULE = BUS1_KAMEN_SUN
    cur_t = 0
    for t in BUSSCHEDULE:
        if t >= cur_hour:
            x = BUSSCHEDULE.index(t)
            time_start_list = [str(BUSSCHEDULE[i]) for i in range(x, x + 5)]
            break
        cur_t += 1
        if cur_t == len(BUSSCHEDULE):
            time_start_list = [str(BUSSCHEDULE[i]) for i in range(-5, 0)]
            break
    # print(bus_num, direction, time_start_list)
    for i in time_start_list:
        hour = int(i[:-2])
        if hour == 24:
            hour = 00
        minute = "{:02d}".format(int(i[-2:]))
        i = time(hour=hour, minute=int(minute))
        arrive_on_busstop_full = datetime.combine(date.today(), i, pytz.UTC) + timedelta(minutes=correction)
        # pytz.utc.localize(arrive_on_busstop_full)
        # pytz.utc.localize(cur_time)
        if arrive_on_busstop_full.time().strftime('%H') == '00':
            arrive_on_busstop_full = arrive_on_busstop_full + timedelta(days=1)
        if cur_hour >= 21 and arrive_on_busstop_full.time().strftime('%H') in ['05', '06', '07', '08', '09']:
            arrive_on_busstop_full = arrive_on_busstop_full + timedelta(days=1)
        if arrive_on_busstop_full >= cur_time:
            x = arrive_on_busstop_full.time().strftime('%H:%M')
            arrive_on_stop.append(x)

    return arrive_on_stop[:3]


# ========= BOT LOGIC ===========
@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.send_message(
    message.chat.id, """\
Привет, я автобусный бот.
Я здесь чтобы рассказать, когда ожидается следующий автобус (никаких гарантий!)
Обо всех замечаниях пишите @EgoriiSt.

Поддерживаемые команды:
/stops - выбрать остановку;

Давайте начнем!\
""")
  print('user_id: ' + str(message.from_user.id))
  print('new user name: ' + str(message.from_user.username))
  lets_start(message)


@bot.message_handler(commands=['stops'])
def lets_start(message):
  keyboard = telebot.types.InlineKeyboardMarkup(row_width=10)
  keyboard.row(
    telebot.types.InlineKeyboardButton('Kamenari', callback_data='Kamenari'))
  keyboard.row(
    telebot.types.InlineKeyboardButton('Bijela', callback_data='Bijela'),
    telebot.types.InlineKeyboardButton('Baosici', callback_data='Baosici'),
    telebot.types.InlineKeyboardButton('Djenovici', callback_data='Djenovici'))
  keyboard.row(
    telebot.types.InlineKeyboardButton('Kumbor', callback_data='Kumbor'),
    telebot.types.InlineKeyboardButton('Zelenika', callback_data='Zelenika'),
    telebot.types.InlineKeyboardButton('Meljine', callback_data='Meljine'))    
  keyboard.row(
    telebot.types.InlineKeyboardButton('Savina', callback_data='Savina'),
    telebot.types.InlineKeyboardButton('Centar', callback_data='Centar'),
    telebot.types.InlineKeyboardButton('Semafor', callback_data='Semafor'))
  keyboard.row(
    telebot.types.InlineKeyboardButton('Igalo Park',
                                       callback_data='IgaloPochta'),
    telebot.types.InlineKeyboardButton('Igalo Institut',
                                       callback_data='IgaloInstitut'))
  keyboard.row(
    telebot.types.InlineKeyboardButton('HDL-VOLI', callback_data='HDLVOLI'))
  print('who is using bot rigth now: ' + str(message.from_user.username))
  bot.send_message(message.chat.id,
                   'Где вы сейчас?',
                   reply_markup=keyboard)

def mainmenu(message):
  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.row(
    telebot.types.InlineKeyboardButton('Выбрать местоположение', callback_data='newcall'))
  bot.send_message(message.chat.id,
                   'Новый запрос?',
                   reply_markup=keyboard)

#   keyboard2 = telebot.types.InlineKeyboardMarkup()
#   keyboard2.row(
#     telebot.types.InlineKeyboardButton('STOP', callback_data='stopbot'),
#     telebot.types.InlineKeyboardButton('START & SET TIME',
#                                        callback_data='settime'))
#   bot.send_message(message.chat.id,
#                    '==== Mission control center: ====',
#                    reply_markup=keyboard2)



# ========== reply to buttons ============
@bot.callback_query_handler(func=lambda call: True)
def dialogue(call):
  if call.data == 'newcall':
    lets_start(call.message)
  msg_tmplt = 0
  user = call.from_user.username
  cur_time = get_current_time()
  cur_hour = int(cur_time.strftime("%H")+'00')
  if cur_hour == 0:
    cur_hour = 2400
  cur_minute = cur_time.strftime("%M")
  day_of_week = cur_time.weekday()
  print('time now is', cur_time)
  bus1toigalo = when_next(call.data, 'Bus1', 'Igalo')
  bus1toigalo_msg = f'🚌1️⃣:  {",  ".join(bus1toigalo)}\n'
  bus1toferry = when_next(call.data, 'Bus1', 'Ferry')
  bus1toferry_msg = f'🚌1️⃣:  {",  ".join(bus1toferry)}\n'

  bus2toigalo = when_next(call.data, 'Bus2', 'Igalo')
  bus2toferry = when_next(call.data, 'Bus2', 'Ferry')
  
  if day_of_week != 6 and bus2toigalo:
    bus2toigalo_msg = f'🚌2️⃣:  {",  ".join(bus2toigalo)}\n'
    bus2toferry_msg = f'🚌2️⃣:  {",  ".join(bus2toferry)}\n'
    msg_tmplt = f'В сторону Каменари (паром ⛴️):\n' \
    f'{bus1toferry_msg}' \
    f'{bus2toferry_msg}\n'\
    f'В сторону Игало (ХДЛ 🛒):\n' \
    f'{bus1toigalo_msg}' \
    f'{bus2toigalo_msg}\n'
  if day_of_week == 6 or not bus2toigalo:
    msg_tmplt = f'В сторону Каменари (паром ⛴️):\n' \
    f'{bus1toferry_msg}\n' \
    f'В сторону Игало (ХДЛ 🛒):\n' \
    f'{bus1toigalo_msg}\n'

  bot.send_message(call.message.chat.id, text=msg_tmplt)
  mainmenu(call.message)
  


keep_alive()  #load flask-server
bot.polling(non_stop=True, interval=0)  #load bot