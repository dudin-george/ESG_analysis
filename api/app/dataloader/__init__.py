from sqlalchemy.ext.asyncio import AsyncSession

from app.dataloader.bank_parser import BankParser
from app.dataloader.broker_parser import BrokerParser
from app.dataloader.insurance_parser import InsuranceParser
from app.dataloader.mfo_parser import MFOParser


async def load_data(db: AsyncSession) -> None:
    # TODO change sessions for each class
    bank = BankParser(db)
    broker = BrokerParser(db)
    insurance = InsuranceParser(db)  # noqa: F841
    mfo = MFOParser(db)
    await bank.load_banks()
    await broker.load_banks()
    await insurance.load_banks()
    await mfo.load_banks()
    # await asyncio.gather(bank.load_banks(), broker.load_banks(), insurance.load_banks(), mfo.load_banks())
