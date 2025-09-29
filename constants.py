import os
import yaml
# yaml separated file need for ignore it for git-github to do not save private data

DEBUG = True # FOR DEBUGGING VIEW

REVERSING = False


if DEBUG:
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


PRIV = {
    'lvl0': config['priveleges']['None'],
    'lvl1': config['priveleges']['User'],
    'lvl2': config['priveleges']['Moderator'],
    'lvl3': config['priveleges']['Admin'],
}

# использовать цикл для этого
ALLOWED_CHAT_IDS = {
    config['allowed_chats']['music_here']: PRIV['lvl3'],
    config['allowed_chats']['fiesta_club']: PRIV['lvl1'],
    config['allowed_chats']['test_chat']: PRIV['lvl1'],
    config['allowed_chats']['my_recs']: PRIV['lvl2'],
    config['allowed_chats']['local']: PRIV['lvl2'],
    #config['allowed_chats']['voenij_osvedomitel']: PRIV['lvl0']
}

ADMIN_USERS = config['admin_users'].values()

COMMANDS = {
    'help_cmd': {
        'command': '/help',
        'privileges': PRIV['lvl1']
    },
    'list_chats_cmd': {
        'command': '/list_chats',
        'privileges': PRIV['lvl3']
    },
    'gpt_cmd': {
        'command': '/ask',
        'privileges': PRIV['lvl1']
    },
    'status_cmd': {
        'command': '/status',
        'privileges': PRIV['lvl2']
    },
    'status_serv_cmd': {
        'command': '/server_status',
        'privileges': PRIV['lvl2']
    },
    # FOR BETA TESTER
    'stats_cmd': {
        'command': '/statistica',
        'privileges': PRIV['lvl1']
    },
}