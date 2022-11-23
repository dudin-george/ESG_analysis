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
class aggregate_table_model_result {
   integer year
   integer quater
   varchar model_name
   varchar source_site
   varchar source_type
   integer neutral
   integer positive
   integer negative
   integer total
   integer id
}

class bank {
   varchar bank_name
   varchar description
   integer bank_type_id
   varchar licence
   integer id
}

class bank_type {
   varchar name
   integer id
}

class model {
   varchar name
   integer model_type_id
   integer id
}

class model_type {
   varchar model_type
   integer id
}

class source {
   varchar site
   integer source_type_id
   varchar parser_state
   timestamp last_update
   integer id
}

class source_type {
   varchar name
   integer id
}

class temp_sentences {
   integer sentence_id
   varchar sentence
   varchar query
   integer id
}

class text {
   varchar link
   integer source_id
   timestamp date
   varchar title
   integer bank_id
   integer comment_num
   integer id
}

class text_result {
   integer text_sentence_id
   integer model_id
   double precision[] result
   boolean is_processed
   integer id
}

class text_sentence {
   integer text_id
   varchar sentence
   integer sentence_num
   integer id
}

bank  -->  bank_type : bank_type_id
model  -->  model_type : model_type_id
source  -->  source_type : source_type_id
temp_sentences  -->  text_sentence : sentence_id
text  -->  bank : bank_id
text  -->  source : source_id
text_result  -->  model : model_id
text_result  -->  text_sentence : text_sentence_id
text_sentence  -->  text : text_id

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

class sravnibankinfo {
   varchar sravni_id
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
