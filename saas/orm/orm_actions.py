from saas.orm.orm_base_model import ORMBaseModel


class ORMActions:

    def get_db_key(self, model_class, default=None):
        return getattr(model_class, '__db_key__', default)

    def get_db_key_and_model_list(self) -> dict:
        db_key_to_models = {}
        for cls in ORMBaseModel.registry.mappers:
            model = cls.class_
            db_key = self.get_db_key(model_class=model)
            table = model.__table__
            db_key_to_models.setdefault(db_key, []).append(table)
        return db_key_to_models

