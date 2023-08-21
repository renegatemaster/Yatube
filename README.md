# Социальная сеть Yatube
_Создавайте и читайте посты, подписывайтесь на любимых авторов и тематические сообщества._

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

Это учебный проект, в котором я осваивал фреймворком Django, языки HTML, CSS, а также учился писать тесты.

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

