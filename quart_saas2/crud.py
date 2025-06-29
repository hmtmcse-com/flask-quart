from sqlalchemy import select, func, update, delete

class CRUD:
    @staticmethod
    async def create(session, obj):
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    @staticmethod
    async def bulk_create(session, objs):
        session.add_all(objs)
        await session.commit()
        for obj in objs:
            await session.refresh(obj)
        return objs

    @staticmethod
    async def get_by_id(session, model, id):
        stmt = select(model).where(model.id == id)
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def update(session, model, id, data: dict):
        stmt = update(model).where(model.id == id).values(**data)
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def bulk_update(session, model, filter_clause, data: dict):
        stmt = update(model).where(filter_clause).values(**data)
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def delete(session, model, id):
        stmt = delete(model).where(model.id == id)
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def bulk_delete(session, model, filter_clause):
        stmt = delete(model).where(filter_clause)
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def paginate(session, model, page:int=1, page_size:int=10):
        stmt = select(model).offset((page-1)*page_size).limit(page_size)
        res = await session.execute(stmt)
        return res.scalars().all()

    @staticmethod
    async def count(session, model):
        stmt = select(func.count()).select_from(model)
        res = await session.execute(stmt)
        return res.scalar()

    @staticmethod
    async def aggregate(session, model, field, func_type:str):
        f = getattr(func, func_type)
        stmt = select(f(getattr(model, field)))
        res = await session.execute(stmt)
        return res.scalar()

    @staticmethod
    async def group_by(session, model, field):
        stmt = select(getattr(model, field), func.count()).group_by(getattr(model, field))
        res = await session.execute(stmt)
        return res.all()
