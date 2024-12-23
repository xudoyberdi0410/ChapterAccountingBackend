Поддерживаемая версия питона 3.12, остальные не пробовал. Скачать пайтон можете <a href="https://www.python.org/downloads/release/python-3128/">тут.</a>

# Локальный запуск
## Установка зависимостей

```bash
pip install -r requirements.txt
```
## Инициализации миграции
```
alembic upgrade head
```
## Запуск в режиме разработки
```bash
python run.py
```
## Запуск в продакшене(Только Unix подобные)
Для начала нужно установить gunicorn
```bash
pip install gunicorn
```
А потом можно уже запускать с использованием gunicorn
```bash
gunicorn -b 0.0.0.0:<port> run:app
```
Вместо `<port>` нужно вписать порт на котором нужно запустить приложения.

# Сборка докер образа
Для сборки можно использовать эту команду:
```bash
docker build .
```
если сборка будет успешной то в конце будет такая надпись `=> => writing image sha256:c58bb14a0df281e2bf23bdc7a19bde581f1dba20ba72d21a4767dcc8bcfb646a                                 0.0s` берем от sha256 до времени.
# Запуск докер образа
```bash
docker run -d -p 8000:8000 <docker_name_or_id>
```