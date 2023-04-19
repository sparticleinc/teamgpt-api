import json
import uuid
from typing import Optional

from tortoise.contrib.pydantic import pydantic_model_creator
from teamgpt import models
from pydantic import BaseModel

from teamgpt.models import StripeProducts

UserOut = pydantic_model_creator(
    models.User,
    name='UserOut',
)

OrganizationOut = pydantic_model_creator(
    models.Organization,
    name='OrganizationOut',
    exclude=(
        'code',
        'code_expiration_time'
    ),
)
OrganizationSuperOut = pydantic_model_creator(
    models.Organization,
    name='OrganizationSuperOut',
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
        'created_at',
        'updated_at',
        'run_time',
        'key'
    ),
)

ConversationsMessageOut = pydantic_model_creator(
    models.ConversationsMessage,
    name='ConversationsMessageOut',
    exclude=(
        'key',
    ),
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
    id: uuid.UUID
    title: str
    description: str
    instruction: str
    user: UserOut

    class Config:
        orm_mode = True


class OrganizationShareOut(BaseModel):
    id: uuid.UUID
    organization: OrganizationOut
    user: UserOut

    class Config:
        orm_mode = True


SysGPTKeyIn = pydantic_model_creator(
    models.SysGPTKey,
    name='SysGPTKeyIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
    ),
)

SysGPTKeyOut = pydantic_model_creator(
    models.SysGPTKey,
    name='SysGPTKeyOut',
)

GptPromptIn = pydantic_model_creator(
    models.GptPrompt,
    name='GptPromptIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
    ),
)

GptPromptOut = pydantic_model_creator(
    models.GptPrompt,
    name='GptPromptOut',
)

GptTopicIn = pydantic_model_creator(
    models.GptTopic,
    name='GptTopicIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
    ),
)

GptTopicOut = pydantic_model_creator(
    models.GptTopic,
    name='GptTopicOut',
)

OpenGptKeyIn = pydantic_model_creator(
    models.OpenGptKey,
    name='OpenGptKeyIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
        'key'
    ),
)
OpenGptKeyOut = pydantic_model_creator(
    models.OpenGptKey,
    name='OpenGptKeyOut',
)

OpenGptConversationsIn = pydantic_model_creator(
    models.OpenGptConversations,
    name='OpenGptConversationsIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
    ),
)

OpenGptConversationsOut = pydantic_model_creator(
    models.OpenGptConversations,
    name='OpenGptConversationsOut',
)

OpenGptChatMessageIn = pydantic_model_creator(
    models.OpenGptChatMessage,
    name='OpenGptChatMessageIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
        'req_message',
        'token',
        'run_time'
    ),
)

OpenGptChatMessageOut = pydantic_model_creator(
    models.OpenGptChatMessage,
    name='OpenGptChatMessageOut',
)

StripeProductsIn = pydantic_model_creator(
    models.StripeProducts,
    name='StripeProductsIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
    ),
)

StripeProductsOut = pydantic_model_creator(
    models.StripeProducts,
    name='StripeProductsOut',
)

StripePaymentsIn = pydantic_model_creator(
    models.StripePayments,
    name='StripePaymentsIn',
    exclude=(
        'id',
        'created_at',
        'updated_at',
    ),
)

StripePaymentsOut = pydantic_model_creator(
    models.StripePayments,
    name='StripePaymentsOut',
)


class StripePaymentsToOut(BaseModel):
    api_id: str
    type: str
    invoice: str
    stripe_products: StripeProductsOut

    class Config:
        orm_mode = True


class GptPromptToOut(BaseModel):
    belong: Optional[list] = None
    prompt_template: str
    prompt_hint: Optional[str] = None
    teaser: str
    title: str
    id: uuid.UUID
    gpt_topic_id: uuid.UUID
    user: Optional[UserOut] = None

    class Config:
        orm_mode = True


class StripeCheckoutIn(BaseModel):
    lookup_key: str
    organization_id: str
