# ESGanalysis
## Описание проекта
TODO
### Добавление модели
Для добавление модели надо положить ее в папку `pretrained_models`
### Добавление парсера
Надо добавить в папку parser и в файле `main.py` запустить функцию для сбора данных с определенной периодичностью. Также надо в папку =db= файл с описанием таблицы.
## Схема бд

``` mermaid
classDiagram
direction BT
class banks {
   varchar bank_name
   varchar bank_status
   varchar description
   varchar id
}
class infobankiru {
   varchar bank_name
   varchar reviews_url
   varchar bank_id
   integer id
}
class models {
   varchar model_path
   integer id
}
class reviews {
   varchar link
   integer rating
   integer source_id
   datetime date
   varchar title
   varchar text
   varchar bank_id
   integer comments_num
   varchar user_id
   boolean processed
   integer id
}
class source {
   varchar site
   datetime last_checked
   varchar description
   integer id
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
class textmodels {
   integer text_id
   integer model_id
}
class textresult {
   integer review_id
   integer sent_num
   varchar sentence
   varchar result
   integer id
}

banks  -->  infobankiru : bank_id
banks  -->  reviews : bank_id
source  -->  reviews : source_id
banks  -->  sravnibankinfo : bank_id
models  -->  textmodels : model_id
textresult  -->  textmodels : text_id
reviews  -->  textresult : review_id
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
