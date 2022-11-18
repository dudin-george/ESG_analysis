from sqlalchemy import Column, Integer, String

from common.database import Base


class VKBaseDB(Base):
    __abstract__ = True

    id = Column(Integer, index=True)
    vk_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    domain = Column(String)


class VkBank(VKBaseDB):
    __tablename__ = "vk_bank_list"

    id = Column(Integer, primary_key=True, index=True)


class VkOtherIndustries(VKBaseDB):
    __tablename__ = "vk_other_industries"

    real_id = Column(Integer, primary_key=True, index=True)
