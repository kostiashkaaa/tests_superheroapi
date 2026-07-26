# Superhero Tallest Finder

Тестовое задание. Нужна была функция, которая по полу героя и по тому,
есть ли у него работа, находит самого высокого героя. Данные берутся из
[superhero-api](https://akabab.github.io/superhero-api/).

## Файлы

- `hero_finder.py` - сама функция и клиент API
- `test_hero_finder.py` - тесты
- `requirements.txt` - зависимости

## Установка

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск тестов

```bash
pytest -v
```

## Использование

```python
from hero_finder import get_tallest_hero

hero = get_tallest_hero(gender="Male", employed=True)
print(hero["name"])
```

В API рост хранится как `["6'8", "203 cm"]`, если неизвестен, то оба
значения будут `"-"`. Такие герои просто не участвуют в сравнении, без
падения программы.

Работа определяется по полю `work.occupation`: значение `"-"` значит, что
работы нет, всё остальное считается работой.

Пол сравнивается без учёта регистра, в реальных данных API попадаются
и "Male", и "male".

`find_tallest_hero` работает с уже готовым списком героев, без похода в
сеть - так её проще тестировать. За сам HTTP-запрос отвечает `fetch_heroes`,
и в тестах `requests.get` подменяется моком, так что реальных запросов при
прогоне тестов не будет.
