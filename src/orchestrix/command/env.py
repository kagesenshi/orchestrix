from pydantic_settings import BaseSettings

class CLISettings(BaseSettings):
    host: str = 'http://localhost:8000'

    class Config:
        env_prefix = 'ORCHESTRIX_'

env = CLISettings()

