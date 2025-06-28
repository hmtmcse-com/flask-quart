import asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String


# Base model
class Base(DeclarativeBase):
    pass


# Our example table
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


# Database connection
engine = create_async_engine("sqlite+aiosqlite:///./basic-crud.sqlite3", echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)


# CRUD functions

async def create_user(name: str):
    async with Session() as session:
        new_user = User(name=name)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


async def read_users_paginated(page: int, page_size: int):
    offset = (page - 1) * page_size
    async with Session() as session:
        stmt = select(User).offset(offset).limit(page_size)
        result = await session.execute(stmt)
        users = result.scalars().all()
        return users


async def update_user(user_id: int, new_name: str):
    async with Session() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(name=new_name)
            .execution_options(synchronize_session="fetch")
        )
        await session.execute(stmt)
        await session.commit()


async def delete_user(user_id: int):
    async with Session() as session:
        stmt = delete(User).where(User.id == user_id)
        await session.execute(stmt)
        await session.commit()


async def main():
    # Create schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # CREATE
    user1 = await create_user("Alice")
    user2 = await create_user("Bob")
    user3 = await create_user("Charlie")
    user4 = await create_user("David")

    print(f"Created users: {user1}, {user2}, {user3}, {user4}")

    # READ paginated
    print("\n-- Page 1 --")
    users_page1 = await read_users_paginated(page=1, page_size=2)
    for user in users_page1:
        print(f"{user.id}: {user.name}")

    print("\n-- Page 2 --")
    users_page2 = await read_users_paginated(page=2, page_size=2)
    for user in users_page2:
        print(f"{user.id}: {user.name}")

    # UPDATE
    await update_user(user_id=1, new_name="Alicia")
    updated_users = await read_users_paginated(page=1, page_size=10)
    print("\n-- After update --")
    for user in updated_users:
        print(f"{user.id}: {user.name}")

    # DELETE
    await delete_user(user_id=2)
    after_delete = await read_users_paginated(page=1, page_size=10)
    print("\n-- After delete --")
    for user in after_delete:
        print(f"{user.id}: {user.name}")


if __name__ == "__main__":
    asyncio.run(main())
