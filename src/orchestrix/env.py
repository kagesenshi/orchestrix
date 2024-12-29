from pydantic_settings import BaseSettings

class OrchestrixSettings(BaseSettings):
    db_url: str = 'sqlite+aiosqlite:///./orchestrix.db'
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_recycle: int = 3600
    db_echo: bool = False
    db_pool_pre_ping: bool = True
    timezone: str = 'UTC'

    class Config:
        env_prefix = 'ORCHESTRIX_'

env = OrchestrixSettings()