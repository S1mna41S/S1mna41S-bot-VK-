import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType

from last_timestamp_reader.timestamp_reader import TimeStampReader

from datetime import datetime
from time import sleep
from random import randint

SENPAI_ID = 120259013
access_token = '59c075e4b6d90dc3774f2af6f0db72a19f6e42cdb7fe23541951e4916de7e76b578d9747d335dd1bd8591'


def get_random_id():
    return randint(0, 2147483646)


def send_attachments_to_chat(attachments):
    """
    Отправляет вложения в беседу с указанным id.
    :param chat_id: id беседы
    :param attachments: список вложений
    """
    attaches = {'photo': [], 'audio': []}
    vk.messages.send(
        chat_id=1,
        message='Сталкеры, внимание! Выброс начнётся с минуты на минуту. Ищите глубокую нору, если жить охота.',
        random_id=get_random_id(),
        attachment='photo-197221192_457239196'
    )
    sleep(6)
    for ata in attachments:
        attaches[ata[:5]].append(ata)
    for i in range(0, len(attaches['audio']), 5):
        response = vk.messages.send(
            chat_id=1,
            attachment=attaches['audio'][i:i + 5],
            random_id=get_random_id()
        )
        print(f'send audios {i}:{i + 5} response - {response}')
        sleep(3)
    for photo in attaches['photo']:
        response = vk.messages.send(
            chat_id=1,
            attachment=photo,
            random_id=get_random_id()
        )
        print(f'send photo {photo} response - {response}')
        sleep(5)
    vk.messages.send(
        chat_id=1,
        message='Всёёё, выброс закончился! Надеюсь, никто не пострадал?',
        random_id=get_random_id(),
        attachment='photo-197221192_457239195'
    )
    vk.messages.send(
        peer_id=SENPAI_ID,
        message='Done',
        random_id=get_random_id()
    )
    print('Выброс закончился')


def get_today_attachments():
    """
    Получает ваши сообщения с вложениями за сегодняшний день.
    :return: список вложений
    """
    today = datetime.now().date()
    history = vk.messages.getHistory(user_id=SENPAI_ID)['items']
    attachments_list = []
    for m in history:
        if 'attachments' in m and datetime.fromtimestamp(m['date']).date() == today:
            for attachment in m['attachments']:
                if attachment['type'] == 'photo':
                    attachments_list.append(
                        f"{attachment['type']}{attachment[attachment['type']]['owner_id']}_{attachment[attachment['type']]['id']}_{attachment['photo']['access_key']}")
                if attachment['type'] == 'audio':
                    attachments_list.append(
                        f"{attachment['type']}{attachment[attachment['type']]['owner_id']}_{attachment[attachment['type']]['id']}")

    return attachments_list


def get_attachments_after_timestamp(timestamp):
    history = vk.messages.getHistory(user_id=SENPAI_ID, count=200)['items']
    new_last_tstamp = history[0]['date']
    attachments_list = []
    for m in history:
        if m['from_id'] != SENPAI_ID:
            continue
        if 'attachments' in m and m['date'] >= timestamp:
            for attachment in m['attachments']:
                if attachment['type'] == 'photo':
                    attachments_list.append(
                        f"{attachment['type']}{attachment[attachment['type']]['owner_id']}_{attachment[attachment['type']]['id']}_{attachment['photo']['access_key']}")
                if attachment['type'] == 'audio':
                    attachments_list.append(
                        f"{attachment['type']}{attachment[attachment['type']]['owner_id']}_{attachment[attachment['type']]['id']}")

    return attachments_list, new_last_tstamp


def handle_message(event):
    """
    Обработчик сообщений бота.
    :param event: событие из LongPoll сервера
    """
    if event.type == VkEventType.MESSAGE_NEW:
        if event.text == '!выброс' and event.peer_id == SENPAI_ID:
            send_new_attachments()


def send_new_attachments():
    tstamp_reader = TimeStampReader()
    last_timestamp = tstamp_reader.get_last_timestamp()
    attachments, new_timestamp = get_attachments_after_timestamp(last_timestamp)
    if attachments:
        send_attachments_to_chat(attachments=attachments)
    else:
        print('Вложений нет')

    tstamp_reader.set_new_timestamp(new_timestamp)


# Авторизация бота
vk_session = vk_api.VkApi(token=access_token)
vk = vk_session.get_api()

longpoll = VkBotLongPoll(vk_session, 197221192)

# Получение id беседы, куда был добавлен бот
# longpoll_settings = vk.groups.getLongPollSettings(group_id=197221192, access_token=access_token)
# chat_ids = longpoll_settings['response']['settings']['api_version']['value']['message_new']['chat_ids']
# chat_id = chat_ids[0]


# Подключение к LongPoll серверу
longpoll = VkLongPoll(vk_session)

# Обработка сообщений
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        handle_message(event)
