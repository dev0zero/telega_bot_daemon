# Перед запуском нужно установить виртуальную среду и все зависимости 

### Устанавливаем привелегии запуска для main.py 
```bash
chmod +x ./main.py
```

### Установить виртуальную среду со всеми зависимостями 

### для linux и macos 
```bash
python3 -m venv venv
source venv/bin/activate
```

### Устанавливаем зависимости в виртуальную среду 
```bash
pip -r install requirements.txt
```


### Чтобы скрипт работал как даемон (ubuntu linux)

#### прописываем в main.py первой строчкой путь до виртуальной среды в которой запускается скрипт

```bash
#!/home/username/path_to_env/venv/bin/python
code ...
```

### после этого делаем его как даемон 

создаем файл с содержимым

```bash
sudo nano /etc/systemd/system/myapp.service
```
файл даемона 
```bash
[Unit]
Description=My Python App Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/python3 /opt/myapp/app.py
Restart=always
RestartSec=5

# Если используется venv:
# ExecStart=/opt/myapp/venv/bin/python app.py

[Install]
WantedBy=multi-user.target
```

процедуры с приложением 
```bash
sudo systemctl daemon-reload
sudo systemctl start|stop|restart|status myapp
journalctl -u myapp -f
```

автозапуск при старте 
```bash
sudo systemctl enable myapp
sudo systemctl disable myapp
```
От корректировать 
```bash
sudo adduser myapp
User=myapp
ExecStart=/opt/myapp/venv/bin/python app.py
After=network-online.target
Wants=network-online.target
```
