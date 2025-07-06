class Config:
    DB_CONNECTION_URI : str = "sqlite+aiosqlite:///default-db.sqlite3"
    DB_MULTI_CONNECTION_URIS : dict[str, str] = {
        "SaaS": "sqlite+aiosqlite:///saas.sqlite3"
    }
    DB_PRINT_LOG: bool = False
    DB_EXPIRE_ON_COMMIT: bool = False

    DB_FUTURE: bool = True # Recommended for SQLAlchemy 2.0 style
    DB_POOL_PRE_PING: bool = True # Check if connections are alive before using them
    DB_POOL_SIZE: int = 5 # Number of concurrent connections to keep in the pool
    DB_MAX_OVERFLOW: int = 10 # Additional connections beyond pool_size (total max 20+30)
    DB_POOL_TIMEOUT: int = 30 # How long (in seconds) to wait for a connection before raising an error
    DB_POOL_RECYCLE: int = -1 # Recycle connections every 30 minutes to avoid stale ones
