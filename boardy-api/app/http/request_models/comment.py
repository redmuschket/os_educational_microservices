from pydantic import BaseModel

class CommentUpdate(BaseModel):
    body: str

class CommentCreate(BaseModel):
    body: str
    author_name: str  # Для curl