#!/bin/bash

echo "Устанавливаем +x для Main.py"
chmod +x ./main.py

echo "запустить виртуальную среду source venv/bin/activate"

echo "Создать виртуальную среду!"
python3 -m venv venv
source venv/bin/activate

