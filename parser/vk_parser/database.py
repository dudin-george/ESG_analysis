from sqlalchemy import Column, Integer, String

from utils.database import Base


class VkBank(Base):
    __tablename__ = "vk_bank_list"

    id = Column(Integer, primary_key=True, index=True)
    vk_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    domain = Column(String)
