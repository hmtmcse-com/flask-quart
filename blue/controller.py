from quart import Blueprint


class BaseController(Blueprint):
    pass

class Controller(BaseController):
    def __init__(self, name: str, url: str):
        super().__init__(
            name=name,
            import_name=__name__,
            url_prefix=url
        )