from saas.orm.orm_base_model import ORMBaseModel
from saas.orm.saas_orm import saas_orm


class Author(ORMBaseModel):
    id: int = saas_orm.Column("id", saas_orm.BigInteger(), primary_key=True, autoincrement=True)
    name: str = saas_orm.Column("name", saas_orm.String(), nullable=False)


class Book(ORMBaseModel):
    id: int = saas_orm.Column("id", saas_orm.Integer(), primary_key=True)
    title: str = saas_orm.Column("title", saas_orm.String(), nullable=False)
    pages: int = saas_orm.Column("pages", saas_orm.Integer())
    authorId: int = saas_orm.Column("author_id", saas_orm.BigInteger(), saas_orm.ForeignKey("Author.id"), nullable=False)
    author = saas_orm.Relationship("Author", back_populates="book")
