from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import MetaData

metadata = MetaData()


@as_declarative(metadata=metadata)
class Base:
    pass
