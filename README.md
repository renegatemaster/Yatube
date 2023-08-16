# Социальная сеть Yatube
Создавайте и читайте посты, подписывайтесь на любимых авторов.

### Как развернуть проект локально?

Клонируем репозиторий и переходим в него в командной строке:

```bash
git clone git@github.com:renegatemaster/Yatube.git
cd yatube
```

Cоздаём и активируем виртуальное окружение, устанавливаем зависимости:

```bash
python3.9 -m venv venv && \ 
    source venv/bin/activate && \
    python -m pip install --upgrade pip && \
    pip install -r backend/requirements.txt
```

Запускаем проект 

```bash
cd yatube/
python3 manage.py runserver
```

