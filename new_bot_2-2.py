import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import json

#выделяет имя игрока из строки [имя]: [роль]
def get_player_name (n_pl):
    return n_pl[:n_pl.find(': ')]
#выделяет роль игрока из строки [имя]: [роль]
def get_player_role(n_pl):
    return n_pl[n_pl.find(': ')+2:]

"""
возвращает всех игроков в строку:
[имя] в роли [роль]
[имя] в роли [роль]
"""
def get_all_players():
    try:
        with open("players.json", "r") as read_file:
            base = ""
            base = json.load(read_file)
            if base != "":
                result = ""
                for i in base:
                    result = result + i[0] + " в роли " + i[1] + '\n'
                read_file.close()
                #не передаём последний символ переноса строки
                return result[:len(result)-1]
            else:
                return "Список пуст."
    except FileNotFoundError:
        return "Список пуст."

def add_many_players(players):
    base = []
    #пробуем открыть файл, если он существует
    try:
        with open("players.json", "r") as read_file:
            base = json.load(read_file)
            read_file.close()
    except FileNotFoundError:
        print("Warning. No JSON file.\n")

    #обрезаем первую строку
    a = players[players.find("\n")+1:]
    #изменяем для удобства все переносы на "/"
    players = a.replace("\n", "/")
    list = []
    #для каждого игрока (кол-во переносов+1)
    for i in range(players.count("/")+1):
        #ищем следующий "/"
        if players.find("/") != -1:
            #есои есть, то берем всё до него
            new_player = players[:players.index("/")]
            #и идаляем из исходной строки
            a = players.replace(new_player+'/', "")
            players = a
        else:
            #иначе берём всё, что осталось
            new_player = players
        if new_player != "" and not new_player.isspace():
            #если "новый игрок" не пуст и не состоит из пробелов, то добавляем его в список
            list.append([get_player_name(new_player), get_player_role(new_player)])
    #пробуем открыть файл, если он существует
    with open("players.json", "w") as write_file:
        #если то, что лежало в файле игроков ранее, пусто (не существует)
        if base == None:
            json.dump(list, write_file)
            write_file.close()
        else:
            #иначе добавляем в конец и пишем в файл
            base.extend(list)
            json.dump(base, write_file)
            write_file.close()

def add_one_player(p):
    #обрезаем команду
    player = p[p.find("добавь ")+7:]
    base = []
    try:
        with open("players.json", "r") as read_file:
            base = json.load(read_file)
            read_file.close()
    except FileNotFoundError:
        print("Warning. No JSON file.")
    #тут у нас base не None, а список, так что даже к пустому можно добавить игрока
    base.append([get_player_name(player), get_player_role(player)])
    with open("players.json", "w") as write_file:
        json.dump(base, write_file)
        write_file.close()

def delete_player(p):
    #обрезаем команду
    player = p[p.find("удали ")+6:]
    try:
        with open("players.json", "r") as read_file:
            base = json.load(read_file)
            read_file.close()
        for i in base:
            #если имя (первый элемент в подсписке [имя]-[роль]) совпадакт с указанныма
            if i[0] == player:
                player_to_remove = i
        if player_to_remove == None:
            return False
        base.remove(player_to_remove)
        with open("players.json", "w") as write_file:
            json.dump(base, write_file)
            write_file.close()
    except FileNotFoundError:
        print("Warning. File not found. Can't delete a player.")
    return True

def group_chat(e):
    msg = e.text
    if msg.find("!бот добавь много") != -1:
        add_many_players(msg)
        vk.messages.send(
            chat_id = e.chat_id,
            random_id=get_random_id(),
            message="Добалены участники. Новый состав:\n"+get_all_players()
        )
    elif msg.find("!бот добавь") != -1:
        add_one_player(msg)
        vk.messages.send(
            chat_id = e.chat_id,
            random_id=get_random_id(),
            message="Новый участник добавлен. Новый состав:\n"+get_all_players()
        )
    elif msg.find("!бот удали") != -1:
        if delete_player(msg):
            vk.messages.send(
                chat_id = e.chat_id,
                random_id=get_random_id(),
                message="Участник удалён"
            )
        else:
            vk.messages.send(
                chat_id = e.chat_id,
                random_id=get_random_id(),
                message="Участник с таким именем не найден"
            )
    elif msg.find("!бот состав") != -1:
        vk.messages.send(
            chat_id = e.chat_id,
            random_id=get_random_id(),
            message="Полный состав:\n"+get_all_players()
        )
    elif msg.find("!бот справка") != -1:
        vk.messages.send(
            chat_id = e.chat_id,
            random_id=get_random_id(),
            message="Обратись ко мне с одной из возможных команд:\n!бот состав\n!бот добавь [имя]: [роль]\n!бот удали [имя]\n!бот добавь много<перенос>[имя]: [роль]<перенос>[имя]: [роль]"
        )
    elif msg.find("!бот привет") != -1:
        vk.messages.send(
            chat_id = e.chat_id,
            random_id=get_random_id(),
            message="Привет)"
        )
    elif msg.find("!бот") != -1:
        vk.messages.send(
            chat_id = e.chat_id,
            random_id=get_random_id(),
            message="Не могу понять команду"
        )
        vk.messages.send(
            chat_id = e.chat_id,
            random_id=get_random_id(),
            message="Обратись ко мне с одной из возможных команд:\n!бот состав\n!бот добавь [имя]: [роль]\n!бот удали [имя]\n!бот добавь много<перенос>[имя]: [роль]<перенос>[имя]: [роль]"
        )

def personal_chat(e):
    vk.messages.send(
        user_id = e.user_id,
        #не знаю точно зачем нужен get_random_id, но без него не работает
        random_id=get_random_id(),
        message="   Добрый день!\nДобавь меня в беседу, в которой тебе требуется моя помощь)"
    )



#сессия
session = requests.Session()

#авторизация (в vk_session можно кинуть логин и пароль от аккаунта, тогда понадобится строчка vk_session.auth())
my_token = "your_token"
k_session = vk_api.VkApi(token = my_token)

#получаем апи
vk = vk_session.get_api()

#штука для просмотра событий
longpoll = VkLongPoll(vk_session)
#рассматриваем каждое новое событие
for event in longpoll.listen():
   #если это сообщение, оно адресовано сообществу/пользователю, под которым зашёл бот, и оно содержит текст
   if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        try:
            #пробуем использовать chat_id, если письмо отправлени лично боту, то при этом обращении возникнет ошибка,
            #и начнётся функция обработки личного сообщения
            if event.chat_id != None:
                group_chat(event)
        except AttributeError:
            personal_chat(event)
