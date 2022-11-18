from enum import Enum


class BankTypeVal(str, Enum):
    bank = "bank"
    broker = "broker"
    insurance = "insurance"
    mfo = "mfo"
