from pydantic import BaseModel


class PostgresConfig(BaseModel):
    host: str
    port: int
    database: str
    user: str
    password: str

    class Config:
        allow_mutation = False
