from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from quart_orm1.db import bind_base, db

BaseModel = bind_base(db)

class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    def as_dict(self):
        return {"id": self.id, "name": self.name}
