from enum import Enum


class BankTypeVal(str, Enum):
    bank = "bank"
    broker = "broker"
    insurance = "insurance"
    mfo = "mfo"

    def __repr__(self) -> str:
        return f"BankTypeVal({self.value})"
