# ⚡ Ultrabot - Быстрый старт (5 минут)

## 🎯 Самый быстрый способ

```bash
# 1. Клонируй репозиторий
git clone https://github.com/kimakorr-gif/Ultrabot.git
cd Ultrabot

# 2. Запусти установку (одна команда!)
./install-setup.sh    # Linux/macOS
# или
install.bat           # Windows

# 3. Заполни .env с твоими данными
nano .env

# Готово! 🎉 Теперь запусти:
./run.sh              # Linux/macOS
# или
run.bat               # Windows
```

## 📋 Что нужно заполнить в .env

Открой `.env` и найди эти строки:

```env
# ❗ ОБЯЗАТЕЛЬНО ЗАПОЛНИ:

# Telegram Bot Token (получи от @BotFather)
TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Твой Telegram канал для постов
TELEGRAM_CHANNEL_ID=-1001234567890

# Yandex Translate API Key
YANDEX_API_KEY=your-api-key-here
YANDEX_FOLDER_ID=your-folder-id-here
```

## 🚀 Проверка

```bash
# Приложение запущено на:
http://localhost:8000

# Проверь здоровье:
curl http://localhost:8000/health

# Должно вывести:
{"status":"ok"}
```

## 🛠️ Полезные команды

```bash
# Просмотр логов
docker-compose logs -f

# Запуск тестов
make test

# Остановка
Ctrl+C

# Полная остановка сервисов
docker-compose down
```

## 📚 Дальше?

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Полное описание (10 минут)
- **[INSTALL_RU.md](INSTALL_RU.md)** - Подробная установка
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Как устроено

## ⚠️ Проблемы?

### "Permission denied" (Linux/macOS)
```bash
chmod +x install-setup.sh run.sh
./install-setup.sh
```

### "Python not found"
```bash
# Установи Python 3.11+
# https://www.python.org/downloads/
python3 --version  # должно быть 3.11+
```

### "docker-compose not found"
```bash
# Установи Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### "Port 8000 in use"
```bash
# Использовать другой порт
uvicorn src.main:app --port 8001
```

## ✅ Готово!

Приложение работает! Читай документацию дальше для углубленного изучения.

---

**Версия**: 1.0  
**Статус**: ✅ Ready to use
