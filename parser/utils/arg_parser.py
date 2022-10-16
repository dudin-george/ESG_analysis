import argparse

from common.base_parser import BaseParser


def parse_args() -> type[BaseParser]:
    """
    Init ArgumentParser
    """
    parser = argparse.ArgumentParser(description="CLI for banks")
    parser.add_argument(
        "--site",
        choices=["sravni_reviews", "banki_reviews", "banki_news", "vk_comments"],
        help="site arguments",
        required=True,
    )
    return _get_class(parser.parse_args())


def _get_class(args: argparse.Namespace) -> type[BaseParser]:
    site = args.site
    match site:
        case "sravni_reviews":
            from sravni_reviews.sravni_reviews import SravniReviews

            return SravniReviews
        case "banki_reviews":
            from banki_ru.reviews_parser import BankiReviews

            return BankiReviews
        case "banki_news":
            from banki_ru.news_parser import BankiNews

            return BankiNews
        case "vk_comments":
            from vk_parser.comments_parser import VKParser

            return VKParser
        case _:
            raise ValueError("Unknown site")
