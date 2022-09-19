# Yatube
## Yatube - социальная сеть, которая даёт пользователям возможность создавать учетную запись, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи.

### Применяемые технологии:
* Python
* Django
* HTML

### Установка проекта

Клонировать репозиторий:

```
git clone https://github.com/Kolupanov/hw05_final.git
```

Перейти в репозиторий в командной строке:

```
cd yatube
```

Cоздать виртуальное окружение:

```
python -m venv venv
```

Активировать виртуальное окружение:

```
source venv/Scripts/activate
```

Установить и обновить систему управления пакетами pip:

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
