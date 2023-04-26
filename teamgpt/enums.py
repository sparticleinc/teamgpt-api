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
    GPT4 = 'gpt-4'


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
