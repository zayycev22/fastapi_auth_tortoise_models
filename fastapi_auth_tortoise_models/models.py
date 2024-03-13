from typing import Type, Optional, Any, Iterable
from tortoise.models import MODEL
from fastapi_auth.models import AbstractToken, AbstractBaseUser, ExternalBaseModel
from tortoise import fields, Model, BaseDBAsyncClient
from fastapi_auth.signals.signal import main_signal


class ExModel(Model, ExternalBaseModel):
    id = fields.IntField(pk=True)

    async def save(self, created: bool = False, using_db: Optional[BaseDBAsyncClient] = None,
                   update_fields: Optional[Iterable[str]] = None,
                   force_create: bool = False,
                   force_update: bool = False, ) -> None:
        await super().save(using_db=using_db, update_fields=update_fields, force_update=force_update,
                           force_create=force_create)
        return await main_signal.emit_after_save(instance=self, created=created)

    @classmethod
    async def create(cls: Type[MODEL], using_db: Optional[BaseDBAsyncClient] = None, **kwargs: Any
                     ) -> MODEL:
        instance = await super().create(using_db=using_db, **kwargs)
        await main_signal.emit_after_save(instance, created=True)
        return instance

    class Meta:
        abstract = True


class BaseUser(Model, AbstractBaseUser):
    id = fields.IntField(pk=True)
    password = fields.CharField(max_length=128)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    time_created = fields.DatetimeField(auto_now_add=True)

    USERNAME_FIELD = ""

    async def save(self, created: bool = False, using_db: Optional[BaseDBAsyncClient] = None,
                   update_fields: Optional[Iterable[str]] = None,
                   force_create: bool = False,
                   force_update: bool = False, ) -> None:
        await super().save(using_db=using_db, update_fields=update_fields, force_update=force_update,
                           force_create=force_create)
        return await main_signal.emit_after_save(instance=self, created=created)

    @classmethod
    async def create(cls: Type[MODEL], using_db: Optional[BaseDBAsyncClient] = None, **kwargs: Any
                     ) -> MODEL:
        instance = await super().create(using_db=using_db, **kwargs)
        await main_signal.emit_after_save(instance, created=True)
        return instance

    class Meta:
        table = "user"
        abstract = True


class User(BaseUser):
    username = fields.CharField(max_length=128, null=False, unique=True)
    USERNAME_FIELD = "username"

    class Meta:
        table = "user"
        abstract = True


class EmailUser(BaseUser):
    email = fields.CharField(max_length=128, null=False, unique=True)
    USERNAME_FIELD = "email"

    class Meta:
        table = "user"
        abstract = True


class Token(Model, AbstractToken):
    id = fields.IntField(pk=True)
    key = fields.CharField(max_length=40, unique=True)
    time_created = fields.DatetimeField(auto_now_add=True)
    user: fields.OneToOneRelation[BaseUser] = fields.OneToOneField("models.User")

    async def save(self, created: bool = False, **kwargs) -> None:
        if not self.key:
            self.key = self.generate_key()
        await super().save(**kwargs)
        return await main_signal.emit_after_save(instance=self, created=created)

    @classmethod
    async def create(cls: Type[MODEL], using_db: Optional[BaseDBAsyncClient] = None, **kwargs: Any
                     ) -> MODEL:
        instance = await super().create(using_db=using_db, **kwargs)
        await main_signal.emit_after_save(instance, created=True)
        return instance

    class Meta:
        abstract = True
        table = "token"
