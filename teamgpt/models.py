from datetime import datetime

from tortoise import fields, models


class AbstractBaseModel(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class AbstractBaseModelWithDeletedAt(AbstractBaseModel):
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True

    async def soft_delete(self):
        self.deleted_at = datetime.now()
        await self.save(update_fields=['deleted_at'])


class User(AbstractBaseModelWithDeletedAt):
    user_id = fields.CharField(max_length=100, unique=True)
    email = fields.CharField(max_length=100, null=True)
    name = fields.CharField(max_length=100, null=True)
    picture = fields.CharField(max_length=255, null=True)
    locale = fields.CharField(max_length=50, null=True)
    nickname = fields.CharField(max_length=100, null=True)

    created_organizations: fields.ReverseRelation['Organization']

    class PydanticMeta:
        exclude = (
            'created_at',
            'updated_at',
            'deleted_at',
            'id'
        )


class Organization(AbstractBaseModelWithDeletedAt):
    name = fields.CharField(max_length=100, unique=True)
    picture = fields.CharField(max_length=255, null=True)
    users = fields.ManyToManyField('models.User', related_name='organizations')
    creator: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User', related_name='created_organizations'
    )

    class PydanticMeta:
        exclude = (
            'created_at',
            'updated_at',
            'deleted_at',
            'id'
        )


class UserOrganization(AbstractBaseModelWithDeletedAt):
    user = fields.ForeignKeyField('models.User', related_name='user_organizations')
    organization = fields.ForeignKeyField('models.Organization', related_name='user_organizations')

    class PydanticMeta:
        exclude = (
            'created_at',
            'updated_at',
            'deleted_at',
            'id'
        )


class GPTKey(AbstractBaseModelWithDeletedAt):
    key = fields.CharField(max_length=255)
    organization = fields.ForeignKeyField('models.Organization', related_name='gpt_keys')

    class PydanticMeta:
        exclude = (
            'created_at',
            'updated_at',
            'deleted_at',
            'id'
        )
