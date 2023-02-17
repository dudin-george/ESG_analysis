from enum import Enum  # in python 3.11 replace with StrEnum


class MdfModels(str, Enum):
    mdf = "mdf_m2"
    mdf_adjusted = "mdf_adjusted"
    mdf_combined = "mdf_combined"
