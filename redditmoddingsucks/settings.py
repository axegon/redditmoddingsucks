from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    username: str = ""
    client_id: str = ""
    client_secret: str = ""
    password: str = ""
    redirect_uri: str = ""
    user_agent: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="REDDITSUCKS_",
        env_file_encoding="utf-8",
    )


settings = Settings()
