from pydantic import BaseModel


class UploadResult(BaseModel):
    url: str
    filename: str
    size: int
    content_type: str
