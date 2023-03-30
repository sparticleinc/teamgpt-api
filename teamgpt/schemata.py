import uuid

from tortoise.contrib.pydantic import pydantic_model_creator
from teamgpt import models
from pydantic import BaseModel

UserOut = pydantic_model_creator(
    models.User,
    name='UserOut',
)

OrganizationOut = pydantic_model_creator(
    models.Organization,
    name='OrganizationOut',
)

OrganizationIn = pydantic_model_creator(
    models.Organization,
    name='OrganizationIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
    ),
)

UserOrganizationIn = pydantic_model_creator(
    models.UserOrganization,
    name='UserOrganizationIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
    ),
)

UserOrganizationOut = pydantic_model_creator(
    models.UserOrganization,
    name='UserOrganizationOut',
)


class UserOrganizationToOut(BaseModel):
    id: uuid.UUID
    role: str
    user: UserOut
    organization: OrganizationOut

    class Config:
        orm_mode = True


class GPTKeyIn(BaseModel):
    key: str
    organization_id: str


GPTKeyOut = pydantic_model_creator(
    models.GPTKey,
    name='GptKeyOut',
)

ConversationsIn = pydantic_model_creator(
    models.Conversations,
    name='ConversationsIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
    ),
)

ConversationsOut = pydantic_model_creator(
    models.Conversations,
    name='ConversationsOut',
)

ConversationsMessageIn = pydantic_model_creator(
    models.ConversationsMessage,
    name='ConversationsMessageIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
        'run_time'
    ),
)

ConversationsMessageOut = pydantic_model_creator(
    models.ConversationsMessage,
    name='ConversationsMessageOut',
)

AiCharacterIn = pydantic_model_creator(
    models.AiCharacter,
    name='AiCharacterIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
    ),
)

AiCharacterOut = pydantic_model_creator(
    models.AiCharacter,
    name='AiCharacterOut',
)


class AiCharacterToOut(BaseModel):
    title: str
    description: str
    instruction: str
    user: UserOut

    class Config:
        orm_mode = True
