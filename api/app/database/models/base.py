from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import as_declarative

metadata = MetaData()


@as_declarative(metadata=metadata)
class Base:
    pass
