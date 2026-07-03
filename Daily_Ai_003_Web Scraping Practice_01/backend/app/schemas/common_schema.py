from pydantic import BaseModel


class Pagination(BaseModel):
    page: int
    pageSize: int
    total: int
    totalPages: int


class ErrorResponse(BaseModel):
    code: str
    message: str


class ErrorWrapper(BaseModel):
    error: ErrorResponse
