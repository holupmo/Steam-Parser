# 🎮 Steam Parser

**Асинхронный парсер скидок в Steam**

Быстрый CLI-инструмент для поиска игр с максимальными скидками. Парсит Steam без API ключа, работает в 10-20 раз быстрее синхронных аналогов.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

---

## ✨ Возможности

- ⚡ **Асинхронный парсинг** — до 20 одновременных запросов
- 🎯 **Фильтрация** — по скидке, цене, жанрам, рейтингу
- 💾 **Кэширование** — повторные запуски мгновенны
- 📊 **Красивый вывод** — цветные таблицы в консоли
- 💰 **Экономия** — показывает сколько денег сэкономил
- 🔗 **Прямые ссылки** — сразу на страницу покупки
- 🚫 **Без API ключа** — работает сразу после установки

---

## 🚀 Быстрый старт

### Установка

```bash
# Клонируем репозиторий
git clone https://github.com/yourname/steam-hunter.git
cd steam-hunter

# Создаём виртуальное окружение
python -m venv venv

# Активируем
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt