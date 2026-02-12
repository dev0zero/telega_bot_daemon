import os
import yaml
# yaml separated file need for ignore it for git-github to do not save private data

DEBUG = True # FOR DEBUGGING VIEW
REVERSING = True
DEBUG_PATH = True
SAVE_MESSAGES_TO_DB = True
DISABLE_DB = True

if DEBUG_PATH:
    CONF = os.path.join(os.path.expanduser('~'), 'PycharmProjects', 'Telega', 'conf_data.yaml')
else:
    CONF = os.path.join(os.path.expanduser('~'), 'Telega', 'conf_data.yaml')

with open(CONF) as f:
    config = yaml.safe_load(f)

# TELEGRAM API AUTH & TELETHON SESSION
if REVERSING: # DEBUG
    # Prod EXEC
    API_ID = config['cgrab_prod']['api_id']
    API_HASH = config['cgrab_prod']['api_hash']
    SESSION_NAME = config['cgrab_prod']['session_name']
else:
    # Test EXEC
    API_ID = config['cgrab_test']['api_id']
    API_HASH = config['cgrab_test']['api_hash']
    SESSION_NAME = config['cgrab_test']['session_name']


# TODO: Зделать выборку, какие api использовать
# data for gemini
GOOGLE_API_KEY = config['ai_api_data']['google']['api_key']
GOOGLE_MODEL_NAME = config['ai_api_data']['google']['model_name']

# DATABASE SETTINGS
HOST = config['database']['host']
DATABASE = config['database']['database']
USER = config['database']['user']
PASSWORD = config['database']['password']
PORT = config['database']['port']
CHARSET = config['database']['charset']

SLEEPTIMER = config['sleeptimer']
WORKINGDIR = config['workingdir']
# TODO: create folder, if not exist

# тут мы устанавливаем привелегии установленым пользователям
# привелегии даются по ссылкам которые указанны в yaml файле
# не обходимо установить тут, потому, что тут иницилизиуются привелегии

ADMINS = config['admini_users']
PRIVILEGES = config['priveleges']
ALLOWED_CHATS = config['chats_allowed']
COMMANDSS = config['commands']

# Инициализируем привелегии указанных пользователей указанные пользователем
for k, v in ADMINS.items():
    for key, value in PRIVILEGES.items():
        if ADMINS[k]['level_id'] == key:
            ADMINS[k]['level_id'] = value
            # break

# Устанавливаем уровни привелегий
privileges_levels = {}
for i,v in PRIVILEGES.items():
    privileges_levels[f"lvl{v}"] = v

# Иницилизируем привелегии чатов которые указанны пользователем в ручную
for key, values in ALLOWED_CHATS.items():
    for kay, value in PRIVILEGES.items():
        if ALLOWED_CHATS[key]['level_id'] == kay:
            ALLOWED_CHATS[key]['level_id'] = value
            # break

# Инициализируем привелееии для всех команд
for k, v in COMMANDSS.items():
    for key, values in PRIVILEGES.items():
        if COMMANDSS[k]['privileges'] == key:
            COMMANDSS[k]['privileges'] = values
