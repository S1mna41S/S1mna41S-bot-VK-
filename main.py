import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType

from last_timestamp_reader.timestamp_reader import TimeStampReader

from datetime import datetime
from time import sleep
from random import randint, choice
import json

SENPAI_ID = 120259013
access_token = '59c075e4b6d90dc3774f2af6f0db72a19f6e42cdb7fe23541951e4916de7e76b578d9747d335dd1bd8591'

PREV_AUDIO_FILE_NAME = 'remaining_audios.json'
PREV_AUDIO_KEY_NAME = 'remaining_audios'


def get_random_id():
    return randint(0, 2147483646)


class exc(Exception):
    pass


def send_attachments_to_chat(attachments):
    """
    Отправляет вложения в беседу с указанным id.
    :param chat_id: id беседы
    :param attachments: список вложений
    """
    if not attachments:
        print('Нечего кидать')
        return

    def time_to_sleep():
        return randint(3, 7)

    attaches = {'photo': [], 'audio': [], 'video': []}
    for ata in attachments:
        # Добавление в словарь вложений по категориям
        attaches[ata[:5]].append(ata)
    messages = ['0'] + attaches['video'] + attaches['photo'] + ['-1']
    audios_on_messages = {i: [] for i in messages}
    remaining_messages = messages
    try:
        for i, audio in enumerate(attaches['audio']):
            while True:
                if not remaining_messages:
                    remaining_audios = attaches['audio'][i:]
                    raise exc
                rand_message = choice(remaining_messages)
                if len(audios_on_messages[rand_message]) < 9:
                    break
                else:
                    remaining_messages.remove(rand_message)

            audios_on_messages[rand_message].append(audio)
    except exc:
        data = {PREV_AUDIO_KEY_NAME: remaining_audios}
        with open(PREV_AUDIO_FILE_NAME, 'w') as f:
            json.dump(data, f)

    vk.messages.send(
        chat_id=1,
        # peer_id=SENPAI_ID,
        message='Сталкеры, внимание! Выброс начнётся с минуты на минуту. Ищите глубокую нору, если жить охота.',
        random_id=get_random_id(),
        attachment=['photo-197221192_457239196'] + audios_on_messages['0']
    )
    sleep(time_to_sleep())

    for photo in (attaches['video'] + attaches['photo']):
        response = vk.messages.send(
            chat_id=1,
            # peer_id=SENPAI_ID,
            attachment=[photo] + audios_on_messages[photo],
            random_id=get_random_id()
        )
        print(f'send photo {photo} response - {response}')
        sleep(time_to_sleep())
    vk.messages.send(
        chat_id=1,
        # peer_id=SENPAI_ID,
        message='Всёёё, выброс закончился! Надеюсь, никто не пострадал?',
        random_id=get_random_id(),
        attachment=['photo-197221192_457239195'] + audios_on_messages['-1']
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
                type = attachment['type']
                if type in ['photo', 'video']:
                    attachments_list.append(
                        f"{type}{attachment[type]['owner_id']}_{attachment[type]['id']}_{attachment[type]['access_key']}")
                if type == 'audio':
                    attachments_list.append(
                        f"{type}{attachment[type]['owner_id']}_{attachment[type]['id']}")

    return attachments_list, new_last_tstamp


def handle_message(event):
    """
    Обработчик сообщений бота.
    :param event: событие из LongPoll сервера
    """
    if event.type == VkEventType.MESSAGE_NEW:
        if event.text == '!выброс' and event.peer_id == SENPAI_ID:
            send_new_attachments()


def _get_previous_attaches():
    with open(PREV_AUDIO_FILE_NAME, 'r') as f:
        data = json.load(f)

    return data[PREV_AUDIO_KEY_NAME]


def send_new_attachments():
    tstamp_reader = TimeStampReader()
    last_timestamp = tstamp_reader.get_last_timestamp()
    attachments, new_timestamp = get_attachments_after_timestamp(last_timestamp)
    prev_audio = _get_previous_attaches()
    attachments = prev_audio + attachments
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
