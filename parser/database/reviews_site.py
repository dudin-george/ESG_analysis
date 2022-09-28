from sqlalchemy import Column, Integer, String

from database import Base


class InfoBankiRu(Base):
    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String)
    reviews_url = Column(String)
    bank_id = Column(String)


class SravniBankInfo(Base):
    id = Column(Integer, primary_key=True, index=True)
    sravni_id: str = Column(String)
    sravni_old_id: int = Column(Integer)
    alias: str = Column(String)
    bank_name: str = Column(String)
    bank_full_name: str = Column(String)
    bank_official_name: str = Column(String)
    bank_id: str = Column(String)
