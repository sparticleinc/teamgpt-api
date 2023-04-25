import uuid
from typing import Optional

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from teamgpt import models

UserOut = pydantic_model_creator(
    models.User,
    name='UserOut',
)


class UserToOut(BaseModel):
    id: uuid.UUID
    user_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
    nickname: Optional[str] = None
    current_organization: Optional[str] = None
    super: Optional[bool] = None
    join_sta: Optional[str] = None

    class Config:
        orm_mode = True


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
    api_id: Optional[str] = None
    type: Optional[str] = None
    invoice: Optional[str] = None
    stripe_products: Optional[StripeProductsOut] = None

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


class OrgPaymentPlanOut(BaseModel):
    is_super: Optional[bool] = False
    is_plan: Optional[bool] = False
    plan_max_number: Optional[int] = 0
    plan_remaining_number: Optional[int] = 0
    is_try: Optional[bool] = False
    try_day: Optional[int] = 0
    is_join: Optional[bool] = False
    expiration_time: Optional[str] = None
    is_send_msg: Optional[bool] = False
    sys_token: Optional[bool] = False


class PaymentPlanInt(BaseModel):
    organization_id: Optional[str] = None
