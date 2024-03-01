# Full Text Search App in Python

Реляционные БД не подходят для поиска:
- Не предназначены для массовых операций чтения над ними из-за их архитектуры.
- Требуют аккуратной работы при поиске по данным. Необходимо построить индексы, проверить запросы — любая ошибка условий в запросах будет сильно замедлять их.

Сервис полнотекстового поиска:
- должен выдерживать высокую нагрузку от пользователей
- обладать гибкими настройками поиска по документам 
- сохранять при этом приемлемое время ответа

поэтому нужно использовать специализированные БД — _поисковые движки_.

**Elasticsearch** выгодно отличается от других поисковых движков:  
Плюсы:  
- Относительная простота установки: готовый docker-образ
- Масштабирование: реплики, шарды, кластер серверов (до 2-3 млн RPS на запись)
- Поисковый движок Apache Lucene: полнотекстовый поиск, нечеткий поиск
- Интерфейс RESTful API
Минусы:  
- Ресурсы (из-за JVM)
- Недостаток безопасности
- Поломки при переходе между мажорными версиями


## Быстрый старт
1. Поднять Elasticsearch + Kibana
```bash
docker compose up -d --remove-orphans
``` 
2. Зайти в Dev Tools  
Вбить в поисковую строку браузера:  
```http://localhost:5601/app/dev_tools#/console```


## Примеры работы с Kibana Dev Tools 
```bash
# Создать индекс
PUT /table
{
  "mappings": {
    "properties": {
      "text_field": {
        "type": "keyword"
      },
      "number": {
        "type": "long"
      }
    }
  }
}
# Сохранить данные
POST /table/_doc/
{
  "text_field": "my pretty text",
  "number": 15
}
```

