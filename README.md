# ESGanalysis
## Описание проекта
TODO
### Добавление модели
Для добавление модели надо положить ее в папку `pretrained_models`
### Добавление парсера
Надо добавить в папку parser и в файле `main.py` запустить функцию для сбора данных с определенной периодичностью. Также надо в папку =db= файл с описанием таблицы.
## Схема бд
### Api
```mermaid
classDiagram
direction BT

class banks {
   varchar bank_name
   varchar bank_status
   varchar description
   varchar id
}

class model_type {
   varchar model_type
   integer id
}

class models {
   varchar model_name
   integer model_type
   integer id
}

class texts {
   varchar link
   integer source_id
   datetime date
   varchar title
   varchar bank_id
   integer comments_num
   integer id
}

class source_type {
    int id
    varchar name
}

class source {
   integer id
   varchar site
   varchar parser_state
   int source_type_id
}

class text_sentences {
    integer id
    integer review_id
    integer sentence_num
    varchar sentence
}

class textresult {
   integer text_sentences_id
   array result
   integer model_id
   integer id
}

texts --> text_sentences: review_id
source_type --> source: id
banks  -->  texts : bank_id
source  -->  texts : source_id
text_sentences --> textresult: text_sentences_id
models --> textresult: model_id
model_type --> models: model_type
```
### Parser service
```mermaid
classDiagram
direction BT

class infobankiru {
   varchar bank_name
   varchar reviews_url
   varchar bank_id
   integer id
}

class parse_sources{
    integer id
    varschar source_name
    datetime parsed
}

class sravnibankinfo {
   varchar(30) sravni_id
   integer sravni_old_id
   varchar alias
   varchar bank_name
   varchar bank_full_name
   varchar bank_official_name
   varchar bank_id
   integer id
}
```
## Команды для разработки

Остановить и удалить все контейнеры
``` shell
docker stop (docker container ls -qa)
docker rm (docker container ls -qa)
```
Тоже остановить все контейнеры
```shell
docker rm $(docker container ls -qa) -f
```

Postgres для локальной разработки
``` shell
docker run --name postgresql -e POSTGRES_USER=myusername -e POSTGRES_PASSWORD=mypassword -p 5432:5432 -d postgres
```
Строки подключения для локальной разработки
```
postgresql+psycopg2://myusername:mypassword@localhost/myusername
sqlite:///database.db
```
Локальный докер с `voluem`
``` shell
docker run --name postgresql -e POSTGRES_USER=myusername -e POSTGRES_PASSWORD=mypassword -p 5432:5432 -v /data:/var/lib/postgresql/data -d postgres
```
## Подключение к БД

```python
import psycopg2
conn = psycopg2.connect(host="localhost", database="database", user="example", password="example", port=5432)
cur = conn.cursor()
cur.execute("SELECT * FROM banks")
cur.fetchone()
# ('ПАОАКБ«1Банк»', '2896', 'ОТЗ', None)
```

## TODO SQL
Запрос объединенный по дате, но без банков
``` postgresql
SELECT
   date,
   sum(result) AS result
FROM
   reviews
   LEFT JOIN
      (
         SELECT
            review_id,
            sum(result[1] - result[3]) AS result
         FROM
            textresult
         GROUP BY
            review_id
      )
      AS query
      ON query.review_id = reviews.id
where
   (result IS NOT NULL) AND (bank_id = '1000')
GROUP BY
     date
```
Запрос объединенный по банкам
``` postgresql
SELECT
   bank_name,
   min(date),
   sum(result) AS result2
FROM
   reviews
   LEFT JOIN
      banks
      ON reviews.bank_id = banks.id
   LEFT JOIN
      (
         SELECT
            review_id,
            sum(result[1] - result[3]) AS result
         FROM
            textresult
         GROUP BY
            review_id
      )
      AS query
      ON query.review_id = reviews.id
GROUP BY
   bank_name
```
