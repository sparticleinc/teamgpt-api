import uuid
from datetime import datetime

from tortoise import fields, models

from teamgpt.enums import Role, ContentType, AutherUser, GptModel


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
    current_organization = fields.CharField(max_length=100, null=True)

    created_organizations: fields.ReverseRelation['Organization']
    user_organizations: fields.ReverseRelation['UserOrganization']
    user_conversations: fields.ReverseRelation['Conversations']
    user_ai_characters: fields.ReverseRelation['AiCharacter']

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

    gpt_keys: fields.ReverseRelation['GPTKey']
    user_user_organizations: fields.ReverseRelation['UserOrganization']
    organization_conversations: fields.ReverseRelation['Conversations']
    organization_ai_characters: fields.ReverseRelation['AiCharacter']

    creator: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User', related_name='created_organizations'
    )

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class UserOrganization(AbstractBaseModelWithDeletedAt):
    user = fields.ForeignKeyField(
        'models.User', related_name='user_organizations')
    organization = fields.ForeignKeyField(
        'models.Organization', related_name='user_user_organizations')
    # 角色
    role = fields.CharEnumField(Role, max_length=100, null=True)

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class GPTKey(AbstractBaseModelWithDeletedAt):
    key = fields.CharField(max_length=255)
    organization = fields.ForeignKeyField(
        'models.Organization', related_name='gpt_keys')

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class Conversations(AbstractBaseModelWithDeletedAt):
    title = fields.CharField(max_length=255)
    organization = fields.ForeignKeyField(
        'models.Organization', related_name='organization_conversations')
    user = fields.ForeignKeyField(
        'models.User', related_name='user_conversations')
    model = fields.CharEnumField(GptModel, max_length=100, null=True)

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class ConversationsMessage(AbstractBaseModelWithDeletedAt):
    message = fields.TextField(null=True)
    conversation = fields.ForeignKeyField(
        'models.Conversations', related_name='conversation_messages')
    user = fields.ForeignKeyField(
        'models.User', related_name='user_messages')
    content_type = fields.CharEnumField(ContentType, max_length=100, null=True)
    author_user = fields.CharEnumField(AutherUser, max_length=100, null=True)
    run_time = fields.IntField(null=True)

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


# ai角色
class AiCharacter(AbstractBaseModelWithDeletedAt):
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    instruction = fields.TextField(null=True)
    organization = fields.ForeignKeyField(
        'models.Organization', related_name='organization_ai_characters')
    user = fields.ForeignKeyField(
        'models.User', related_name='user_ai_characters')

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )
