#!/home/jcmax/Telega/venv/bin/python

from telegram import TelegramWatcher

if __name__ == '__main__':
    watcher = TelegramWatcher()
    watcher.run()
