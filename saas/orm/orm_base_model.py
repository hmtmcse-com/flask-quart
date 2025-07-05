import re
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


def camel_to_snake_case(name: str) -> str:
    """Convert a ``CamelCase`` name to ``snake_case``."""
    name = re.sub(r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))", r"_\1", name)
    return name.lower().lstrip("_")


class ORMBaseModel(DeclarativeBase, MappedAsDataclass):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "__tablename__"):
            cls.__tablename__ = camel_to_snake_case(cls.__name__)
