from saas.orm.orm_actions import ORMActions
from saas.orm.orm_properties import ORMProperties


class SaaSORM(ORMProperties, ORMActions):
    pass



saas_orm = SaaSORM()