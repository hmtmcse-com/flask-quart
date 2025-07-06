from saas.config import Config
from saas.orm.orm_base_model import ORMBaseModel
from saas.orm.orm_data import DBConnectionData


class ORMActions:
    connection_data: dict[str, DBConnectionData] = {}

    def get_model_db_key(self, model_class, default=None):
        return getattr(model_class, '__db_key__', default)

    def get_engine_db_key(self, default=None):
        # Will handle Tenant resolver
        return default

    def get_engine_connection_data(self, db_key: str | None) -> DBConnectionData | None:

        if db_key in self.connection_data:
            return self.connection_data[db_key]

        connection = DBConnectionData(uri=Config.DB_CONNECTION_URI)
        connection.poolSize = Config.DB_POOL_SIZE
        connection.poolPrePing = Config.DB_POOL_PRE_PING
        connection.printLog = Config.DB_PRINT_LOG
        connection.maxOverflow = Config.DB_MAX_OVERFLOW
        connection.poolTimeout = Config.DB_POOL_TIMEOUT
        connection.poolRecycle = Config.DB_POOL_RECYCLE
        connection.expireOnCommit = Config.DB_EXPIRE_ON_COMMIT
        connection.future = Config.DB_FUTURE

        connection_data = None
        if db_key is None:
            connection_data = connection
        elif db_key and isinstance(db_key, str) and Config.DB_MULTI_CONNECTION_URIS and db_key in Config.DB_MULTI_CONNECTION_URIS:
            connection.uri = Config.DB_MULTI_CONNECTION_URIS[db_key]
            connection_data = connection
        # Resolve Database Connection From Here
        if connection_data is not None:
            self.connection_data[db_key] = connection_data

        return connection_data

    def get_db_key_and_model_list(self) -> dict:
        db_key_to_models = {}
        for cls in ORMBaseModel.registry.mappers:
            model = cls.class_
            db_key = self.get_model_db_key(model_class=model)
            table = model.__table__
            db_key_to_models.setdefault(db_key, []).append(table)
        return db_key_to_models
