from orchestrix.db import db_engine
from sqlmodel import SQLModel
from orchestrix.service.tenant.model import Tenant
from orchestrix.service.host.model import Host
import asyncio

async def main():
    engine = db_engine()
    async with engine.connect() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
        await conn.commit()

asyncio.run(main())