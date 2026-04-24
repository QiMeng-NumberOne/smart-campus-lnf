from pydantic import BaseModel


class IdCardInfoIn(BaseModel):
    name: str
    id_no: str | None = None
    student_no: str | None = None
    college: str | None = None
    major: str | None = None
    address: str | None = None
    doc_type: str | None = None
    source: str = "manual"


class IdCardOcrRequest(BaseModel):
    image_url: str
