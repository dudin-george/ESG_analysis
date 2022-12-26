import pytest


@pytest.fixture
def banki_banks_list() -> tuple[str, dict]:
    return "https://www.banki.ru/widget/ajax/bank_list.json", {"data": [{"id": 1, "name": "uni",
                                                                         "licence": "1",
                                                                         "code": "uni", "bank_id": 1,
                                                                         "bank_name": "uni",
                                                                         }, {"id": 1000, "name": "vtb",
                                                                             "licence": "1000",
                                                                             "code": "vtb", "bank_id": 1000,
                                                                             "bank_name": "vtb",
                                                                             }, ]}


@pytest.fixture
def unicredit_reviews_response() -> tuple[str, dict]:
    return "https://www.banki.ru/services/responses/list/ajax/", {"data": [{"id": 10721721, "dateCreate": "2022-10-08 16:05:01",
                      "text": "<p>Клиент Юникредита c с…онков, ни сообщений.</p>",
                      "title": "<p>Клиент Юникредита c с…онков, ни сообщений.</p>",
                      "grade": 1, "isCountable": True, "resolutionIsApproved": None,
                      "commentCount": 4, "company": {"id": 4045, "code": "unicreditbank",
                                                     "name": "unicreditbank",
                                                     "url": "unicreditbank",
                                                     }},
                     {"id": 10720416, "dateCreate": "2022-10-04 15:46:32",
                      "text": "Сегодня выяснилась еще одна новинка от ЮниКредит Банк. На сайте банка публикуется одна ставка, но при размещении депозита вы ее не получаете. Сегодня нам было предложено 0,63% вместо 2,1%, заявленного на сайте банка. \r\n\r\nНикаких комментариев при этом не предоставляется. До текущего момента подобных ситуаций не возникало. С начала года и до текущего времени оборот по депозитным сделкам составляет несколько миллиардов.",
                      "title": "Ставки на сайте банка не…ствуют действительности",
                      "grade": 1, "isCountable": True, "resolutionIsApproved": None,
                      "commentCount": 4, "company": {"id": 4045, "code": "unicreditbank",
                                                     "name": "unicreditbank",
                                                     "url": "unicreditbank",
                                                     }},
                     ],
            "total": 4443
            }
