import argparse
from enum import Enum

from common.base_parser import BaseParser


class ParserType(str, Enum):
    sravni_reviews = "sravni_reviews"
    banki_reviews = "banki_reviews"
    banki_news = "banki_news"
    banki_insurance = "banki_insurance"
    banki_mfo = "banki_mfo"
    banki_broker = "banki_broker"
    vk_comments = "vk_comments"
    irecommend_reviews = "irecommend_reviews"


def parse_args() -> type[BaseParser]:
    """
    Init ArgumentParser
    """
    parser = argparse.ArgumentParser(description="CLI for banks")
    parser.add_argument(
        "--site",
        choices=[parser_type for parser_type in ParserType],
        help="site arguments",
        required=True,
    )
    return _get_class(parser.parse_args())


def _get_class(args: argparse.Namespace) -> type[BaseParser]:
    site = args.site
    match site:
        case ParserType.sravni_reviews:
            from sravni_reviews.sravni_reviews import SravniReviews

            return SravniReviews
        case ParserType.banki_reviews:
            from banki_ru.reviews_parser import BankiReviews

            return BankiReviews
        case ParserType.banki_news:
            from banki_ru.news_parser import BankiNews

            return BankiNews
        case ParserType.banki_insurance:
            from banki_ru.insurance_parser import BankiInsurance

            return BankiInsurance
        case ParserType.banki_broker:
            from banki_ru.broker_parser import BankiBroker

            return BankiBroker
        case ParserType.banki_mfo:
            from banki_ru.mfo_parser import BankiMfo

            return BankiMfo
        case ParserType.vk_comments:
            from vk_parser.comments_parser import VKParser

            return VKParser
        case ParserType.irecommend_reviews:
            from irecommend_reviews.reviews_paresr import IRecommendReviews

            return IRecommendReviews
        case _:
            raise ValueError("Unknown site")
