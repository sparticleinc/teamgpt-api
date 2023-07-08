from datetime import datetime

from tortoise import fields, models

from teamgpt.enums import Role, ContentType, AutherUser, GptModel, StripeModel


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
    super = fields.BooleanField(default=False, null=True)

    created_organizations: fields.ReverseRelation['Organization']
    user_organizations: fields.ReverseRelation['UserOrganization']
    user_conversations: fields.ReverseRelation['Conversations']
    user_ai_characters: fields.ReverseRelation['AiCharacter']
    user_gpt_chat_messages: fields.ReverseRelation['GptChatMessage']
    user_gpt_prompt: fields.ReverseRelation['GptPrompt']

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
    gpt_key_source = fields.CharField(max_length=255, null=True)
    code = fields.CharField(max_length=255, null=True)
    code_expiration_time = fields.DatetimeField(null=True)
    super = fields.BooleanField(default=False, null=True)
    users = fields.ManyToManyField('models.User', related_name='organizations')
    gpt_models = fields.JSONField(null=True)

    gpt_keys: fields.ReverseRelation['GPTKey']
    user_user_organizations: fields.ReverseRelation['UserOrganization']
    organization_conversations: fields.ReverseRelation['Conversations']
    organization_ai_characters: fields.ReverseRelation['AiCharacter']
    organization_gpt_chat_messages: fields.ReverseRelation['GptChatMessage']
    organization_gpt_prompt: fields.ReverseRelation['GptPrompt']
    organization_gpt_topic: fields.ReverseRelation['GptTopic']
    user_gpt_topic: fields.ReverseRelation['GptTopic']

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


class SysGPTKey(AbstractBaseModelWithDeletedAt):
    key = fields.CharField(max_length=255)
    remarks = fields.CharField(max_length=255, null=True)

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
    conversation_gpt_chat_messages: fields.ReverseRelation['GptChatMessage']
    conversation_messages: fields.ReverseRelation['ConversationsMessage']

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class ConversationsMessage(AbstractBaseModelWithDeletedAt):
    message = fields.TextField(null=True)
    shown_message = fields.TextField(null=True)
    conversation = fields.ForeignKeyField(
        'models.Conversations', related_name='conversation_messages')
    user = fields.ForeignKeyField(
        'models.User', related_name='user_messages')
    content_type = fields.CharEnumField(ContentType, max_length=100, null=True)
    author_user = fields.CharEnumField(AutherUser, max_length=100, null=True)
    run_time = fields.IntField(null=True)
    key = fields.CharField(max_length=255, null=True)
    prompt_tokens = fields.IntField(null=True)
    completion_tokens = fields.IntField(null=True)
    total_tokens = fields.IntField(null=True)
    model = fields.CharEnumField(GptModel, max_length=100, null=True)

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


class GptChatMessage(AbstractBaseModelWithDeletedAt):
    in_message = fields.TextField(null=True)
    out_message = fields.TextField(null=True)
    token_num = fields.IntField(null=True, default=0)
    key = fields.CharField(max_length=255, null=True)
    conversation = fields.ForeignKeyField(
        'models.Conversations', related_name='conversation_gpt_chat_messages')
    organization = fields.ForeignKeyField(
        'models.Organization', related_name='organization_gpt_chat_messages')
    user = fields.ForeignKeyField(
        'models.User', related_name='user_gpt_chat_messages')
    prompt_tokens = fields.IntField(null=True)
    completion_tokens = fields.IntField(null=True)
    total_tokens = fields.IntField(null=True)
    model = fields.CharEnumField(GptModel, max_length=100, null=True)

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class GptTopic(AbstractBaseModelWithDeletedAt):
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    pid = fields.UUIDField(null=True)

    organization = fields.ForeignKeyField(
        'models.Organization', related_name='organization_gpt_topic', null=True)
    user = fields.ForeignKeyField(
        'models.User', related_name='user_gpt_topic', null=True)

    gpt_topic_gpt_prompt: fields.ReverseRelation['GptPrompt']

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class GptPrompt(AbstractBaseModelWithDeletedAt):
    belong = fields.JSONField(null=True)
    prompt_template = fields.TextField(null=True)
    prompt_hint = fields.TextField(null=True)
    teaser = fields.TextField(null=True)
    title = fields.CharField(max_length=255, null=True)
    zh_CN_prompt_template = fields.TextField(null=True)
    zh_CN_prompt_hint = fields.TextField(null=True)
    zh_CN_teaser = fields.TextField(null=True)
    zh_CN_title = fields.CharField(max_length=255, null=True)
    gpt_topic = fields.ForeignKeyField(
        'models.GptTopic', related_name='gpt_topic_gpt_prompt', null=True)
    organization = fields.ForeignKeyField(
        'models.Organization', related_name='organization_gpt_prompt', null=True)
    user = fields.ForeignKeyField(
        'models.User', related_name='user_gpt_prompt', null=True)

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class OpenGptKey(AbstractBaseModelWithDeletedAt):
    key = fields.CharField(max_length=255)
    gpt_key = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255, null=True)

    open_gpt_key_conversations: fields.ReverseRelation['OpenGptConversations']
    open_gpt_key_messages: fields.ReverseRelation['OpenGptConversationsMessage']

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class OpenGptConversations(AbstractBaseModelWithDeletedAt):
    title = fields.CharField(max_length=255)
    model = fields.CharEnumField(GptModel, max_length=100, null=True)

    open_gpt_key = fields.ForeignKeyField(
        'models.OpenGptKey', related_name='open_gpt_key_conversations')

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class OpenGptConversationsMessage(AbstractBaseModelWithDeletedAt):
    message = fields.TextField(null=True)
    content_type = fields.CharEnumField(ContentType, max_length=100, null=True)
    author_user = fields.CharEnumField(AutherUser, max_length=100, null=True)
    run_time = fields.IntField(null=True)

    open_gpt_key = fields.ForeignKeyField(
        'models.OpenGptKey', related_name='open_gpt_key_messages')

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class OpenGptChatMessage(AbstractBaseModelWithDeletedAt):
    open_gpt_key = fields.ForeignKeyField(
        'models.OpenGptKey', related_name='open_gpt_key_chat_messages')
    model = fields.CharEnumField(GptModel, max_length=100, null=True)
    temperature = fields.IntField(null=True)
    top_p = fields.IntField(null=True)
    n = fields.IntField(null=True)
    stream = fields.BooleanField(null=True)
    stop = fields.CharField(max_length=100, null=True)
    max_tokens = fields.IntField(null=True)
    presence_penalty = fields.IntField(null=True)
    frequency_penalty = fields.IntField(null=True)
    messages = fields.JSONField(null=True)
    req_message = fields.TextField(null=True)
    run_time = fields.IntField(null=True)
    prompt_tokens = fields.IntField(null=True)
    completion_tokens = fields.IntField(null=True)
    total_tokens = fields.IntField(null=True)
    logit_bias = fields.JSONField(null=True)
    user = fields.CharField(max_length=255, null=True)

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )


class StripeWebhookLog(AbstractBaseModelWithDeletedAt):
    type = fields.CharField(max_length=255, null=True)
    data = fields.JSONField(null=True)
    run_sta = fields.CharField(max_length=255, null=True)


class StripeProducts(AbstractBaseModelWithDeletedAt):
    name = fields.CharField(max_length=255, null=True)
    max_number = fields.IntField(null=True, default=0)
    max_tokens = fields.IntField(null=True, default=0)
    sys_token = fields.BooleanField(null=True, default=False)
    api_id = fields.CharField(max_length=255, null=True)
    order = fields.IntField(null=True, default=0)
    month = fields.IntField(null=True, default=0)
    mode = fields.CharEnumField(
        StripeModel, null=True, default=StripeModel.SUBSCRIPTION)
    product = fields.CharField(max_length=255, null=True)


class StripePayments(AbstractBaseModelWithDeletedAt):
    api_id = fields.CharField(max_length=255, null=True)
    sub_id = fields.CharField(max_length=255, null=True)
    payment_id = fields.CharField(max_length=255, null=True)
    mode = fields.CharEnumField(
        StripeModel, null=True, default=StripeModel.SUBSCRIPTION)
    type = fields.CharField(max_length=255, null=True)
    invoice = fields.CharField(max_length=255, null=True)
    customer_details = fields.JSONField(null=True)
    stripe_products = fields.ForeignKeyField('models.StripeProducts', related_name='stripe_products_stripe_payments',
                                             null=True)
    organization = fields.ForeignKeyField(
        'models.Organization', related_name='organization_stripe_payments', null=True)
    user = fields.ForeignKeyField(
        'models.User', related_name='user_stripe_payments', null=True)


class MidjourneyProxySubmit(AbstractBaseModelWithDeletedAt):
    action = fields.CharField(max_length=50, null=True)
    prompt = fields.TextField(null=True)
    taskId = fields.CharField(max_length=255, null=True)
    index = fields.IntField(max_length=50, null=True)
    state = fields.CharField(max_length=50, null=True)
    notifyHook = fields.CharField(max_length=255, null=True)
    req_code = fields.IntField(max_length=50, null=True)
    req_description = fields.CharField(max_length=255, null=True)
    req_result = fields.CharField(null=True, max_length=255)
    status = fields.CharField(null=True, max_length=255, default='IN_PROGRESS')
    image_url = fields.CharField(null=True, max_length=255)
    finish_time = fields.CharField(null=True, max_length=255)
    user = fields.ForeignKeyField(
        'models.User', related_name='user_submit', null=True)
    organization = fields.ForeignKeyField(
        'models.Organization', related_name='organization_submit', null=True)


class MidjourneyProxySubmitUv(AbstractBaseModelWithDeletedAt):
    state = fields.CharField(max_length=50, null=True)
    content = fields.CharField(max_length=50, null=True)
    notifyHook = fields.CharField(max_length=255, null=True)
    req_code = fields.IntField(max_length=50, null=True)


class MidjourneyProxyHook(AbstractBaseModelWithDeletedAt):
    run_id = fields.CharField(max_length=255, null=True)
    action = fields.CharField(max_length=255, null=True)
    prompt = fields.CharField(max_length=255, null=True)
    promptEn = fields.CharField(max_length=255, null=True)
    description = fields.CharField(max_length=255, null=True)
    state = fields.CharField(max_length=255, null=True)
    submitTime = fields.CharField(max_length=255, null=True)
    finishTime = fields.CharField(max_length=255, null=True)
    imageUrl = fields.CharField(max_length=255, null=True)
    status = fields.CharField(max_length=255, null=True)

    midjourney_proxy_submit = fields.ForeignKeyField(
        'models.MidjourneyProxySubmit', related_name='midjourney_proxy_submit_hook', null=True)


class SystemConfig(AbstractBaseModelWithDeletedAt):
    name = fields.CharField(max_length=255, null=True)
    value = fields.JSONField(max_length=255, null=True)
    description = fields.CharField(max_length=255, null=True)
    type = fields.CharField(max_length=255, null=True)
    order = fields.IntField(null=True)
    info = fields.JSONField(null=True)


class UserAttribute(AbstractBaseModelWithDeletedAt):
    title = fields.CharField(max_length=255, null=True)
    value = fields.CharField(max_length=255, null=True)
    answer = fields.CharField(max_length=255, null=True)

    user = fields.ForeignKeyField('models.User', related_name='user_user_attribute', null=True)

    class PydanticMeta:
        exclude = (
            'updated_at',
            'deleted_at',
        )
