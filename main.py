from parser.Sravni import Sravni

from model.Database import Database


def main() -> None:
    Database()

    sravni_parser = Sravni()
    sravni_parser.parse()


if __name__ == "__main__":
    main()
