from app.dto import ModelType
from app.models.base_mdf import BaseMDF


class MDF(BaseMDF):
    name = ModelType.mdf
    file_path = "mdf_v2.csv.zip"
