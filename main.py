from time import sleep
from random import randint, choice
import json
from collections import defaultdict
from random import shuffle

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.longpoll import VkLongPoll, VkEventType

SENPAI_ID = 120259013
STARTERS_ID = [SENPAI_ID, 209523958]
PEERS_ID = [SENPAI_ID, 209523958]
access_token = '59c075e4b6d90dc3774f2af6f0db72a19f6e42cdb7fe23541951e4916de7e76b578d9747d335dd1bd8591'
users_score = {}

PREV_AUDIO_FILE_NAME = 'remaining_audios.json'
PREV_AUDIO_KEY_NAME = 'remaining_audios'

DONE = 'Done.'


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

    print('Вложения найдены!')
    print("Отправляю титры")
    meme_names = ['Конченный идиот',
                  'Самый сексуальный мужик в мире',
                  'Горячая чикса',
                  'Злодей-британец',
                  'Так себе шутник',
                  'Пубертатная язва',
                  'Какой-то мужик']
    shuffle(meme_names)
    name_for_others = 'Недопонятые гении'
    vk.messages.send(
        chat_id=1,
        message='В главных ролях: ',
        random_id=get_random_id()
    )
    sleep(1)
    # Удаление ключей, где сумма значений во вложенных словарях равна нулю
    filtered_data = {k: v for k, v in users_score.items() if sum(v.values()) != 0}
    sorted_users_score = dict(sorted(filtered_data.items(), key=lambda item: sum(item[1].values()), reverse=True))
    for user_id, meme in zip(sorted_users_score.keys(), meme_names):
        # Получение информации о пользователе
        user_info = vk.users.get(user_ids=user_id)[0]
        # Извлечение имени и фамилии пользователя
        first_name = user_info['first_name']
        last_name = user_info['last_name']
        attaches_message = ''
        for attach in sorted_users_score[user_id]:
            attaches_message += f'{sorted_users_score[user_id][attach]} {attach} '
        vk.messages.send(
            chat_id=1,
            message=f'{meme}: {last_name} {first_name}\n{attaches_message}',
            random_id=get_random_id()
        )
        sleep(time_to_sleep())
    if len(sorted_users_score) > len(meme_names):
        message = name_for_others + ':\n'
        for user_id in list(sorted_users_score[len(meme_names):]):
            # Получение информации о пользователе
            user_info = vk.users.get(user_ids=user_id)[0]
            # Извлечение имени и фамилии пользователя
            first_name = user_info['first_name']
            last_name = user_info['last_name']
            attaches_message = ''
            for attach in sorted_users_score[user_id]:
                attaches_message += f'{sorted_users_score[user_id][attach]} {attach} '
            message += f'\n{last_name} {first_name}\n{attaches_message}'
        vk.messages.send(
            chat_id=1,
            message=message,
            random_id=get_random_id()
        )
    attaches = {'photo': [], 'audio': [], 'video': []}
    attaches2log = {'photo': 'фото', 'audio': 'аудио', 'video': 'видео'}
    for ata in attachments:
        # Добавление в словарь вложений по категориям
        attaches[ata[:5]].append(ata)
    print('Сегодня у нас в меню...')
    for ata_type in attaches:
        if attaches[ata_type]:
            print(f'{len(attaches[ata_type])} {attaches2log[ata_type]}')

    print('Последние подготовки...')
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

    print('Выброс начинается...')
    vk.messages.send(
        chat_id=1,
        # peer_id=SENPAI_ID,
        message='Сталкеры, внимание! Выброс начнётся с минуты на минуту. Ищите глубокую нору, если жить охота.',
        random_id=get_random_id(),
        attachment=['photo-197221192_457239196'] + audios_on_messages['0']
    )
    sleep(time_to_sleep())

    for photo in (attaches['photo'] + attaches['video']):
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
    for user_id in filtered_data:
        vk.messages.send(
            peer_id=user_id,
            message=DONE,
            random_id=get_random_id()
        )
    print('Выброс закончился')


def get_attachment():
    history = []
    # Получение списка всех диалогов
    conversations = vk.messages.getConversations()['items']
    for conversation in conversations:
        # Получение истории с каждым юзером
        peer_id = conversation['conversation']['peer']['id']
        users_score[peer_id] = defaultdict(int)
        history.extend(vk.messages.getHistory(user_id=peer_id, count=200)['items'])
    history.sort(key=lambda x: -x['date'])
    attachments_list = []
    for m in history:
        if m['text'] != DONE:
            for attachment in m['attachments']:
                type = attachment['type']
                if type in ['photo', 'video']:
                    if 'access_key' in attachment[type]:
                        attachments_list.append(
                            f"{type}{attachment[type]['owner_id']}_{attachment[type]['id']}_{attachment[type]['access_key']}"
                        )
                    else:
                        attachments_list.append(f"{type}{attachment[type]['owner_id']}_{attachment[type]['id']}")
                if type == 'audio':
                    attachments_list.append(
                        f"{type}{attachment[type]['owner_id']}_{attachment[type]['id']}")
                users_score[m['from_id']][type] += 1
        else:
            break

    return attachments_list


def handle_message(event):
    """
    Обработчик сообщений бота.
    :param event: событие из LongPoll сервера
    """
    if event.type == VkEventType.MESSAGE_NEW:
        if event.text == '!выброс' and event.peer_id in STARTERS_ID:
            send_new_attachments()


def _get_previous_attaches():
    with open(PREV_AUDIO_FILE_NAME, 'r') as f:
        data = json.load(f)

    return data[PREV_AUDIO_KEY_NAME]


def send_new_attachments():
    print('Стартуем!')
    print('Ищутся последние вложения...')
    attachments = get_attachment()
    prev_audio = _get_previous_attaches()
    attachments = prev_audio + attachments
    if attachments:
        send_attachments_to_chat(attachments=attachments)
    else:
        print('Вложений нет')


print('Включаем бота...')
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

print('Бот ждёт команды')
# Обработка сообщений
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        handle_message(event)
