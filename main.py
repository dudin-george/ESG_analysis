from parser.SravniReviews import SravniReviews

from model.Database import Database


def main() -> None:
    Database()

    sravni_parser = SravniReviews()
    sravni_parser.parse()


if __name__ == "__main__":
    main()
