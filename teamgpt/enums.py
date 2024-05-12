from enum import Enum


class Role(str, Enum):
    CREATOR = 'creator'
    MEMBER = 'member'


class ContentType(str, Enum):
    TEXT = 'text'
    IMAGE = 'image'
    AUDIO = 'audio'
    VIDEO = 'video'


class AutherUser(str, Enum):
    USER = 'user'
    SYSTEM = 'system'
    ASSISTANT = 'assistant'


class GptModel(str, Enum):
    GPT3 = 'gpt-3'
    GPT3TURBO = 'gpt-3.5-turbo'
    GPT3TURBO0613 = 'gpt-3.5-turbo-0613'
    GPT3TURBO_16K_0613 = 'gpt-3.5-turbo-16k-0613'
    GPT3TURBO_16K = 'gpt-3.5-turbo-16k'
    GPT4 = 'gpt-4'
    GPT4_0613= 'gpt-4-0613'
    GPT4_32K= 'gpt-4-32k'
    GPT4_32K_0613= 'gpt-4-32k-0613'
    GPT4_0125= 'gpt-4-0125-preview'
    GPT3_0125= 'gpt-3.5-turbo-0125'
    GPT4_TURBO = 'gpt-4-turbo'


class GptKeySource(str, Enum):
    SYSTEM = 'system'
    ORG = 'org'


class Belong(str, Enum):
    ORG = 'org'
    OWN = 'own'
    PUBLIC = 'public'


class StripeModel(str, Enum):
    PAYMENT = 'payment'
    SUBSCRIPTION = 'subscription'
