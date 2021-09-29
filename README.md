# Бот StuffExchanger

Бот для Телеграма, который позволяет обменять что-то ненужное на очень нужное.


## Требования

Для запуска вам понадобится Python 3.6 или выше.

Необходимо зарегистрировать бота и получить токен для доступа к API Телеграма. Подробная инструкция [как зарегистрировать бота](https://way23.ru/%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B1%D0%BE%D1%82%D0%B0-%D0%B2-telegram/)

## Переменные окружения

Настройки берутся из переменных окружения. Чтобы их определить, создайте файл `.env` рядом с `main.py` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

Доступные переменные:

- `TG_TOKEN` — токен бота, который будет постить картинки. 

Пример:

```env
TG_TOKEN=2013730263:AdFh2f5udX9cfYqo2NYLkr3anr2yEKwKPk
```

## Запуск

Скачайте код с GitHub. Установите зависимости:

```sh
pip install -r requirements.txt
```

### Запустите скрипт:
```sh
python main.py
```

## Цели проекта

Код написан в учебных целях — для курса по Python на сайте [Devman](https://dvmn.org).