from pydantic import BaseModel


class ActivateKeySchema(BaseModel):
    activation_key: str


class VMResponse(BaseModel):
    host: str
    port: int
    protocol: str
