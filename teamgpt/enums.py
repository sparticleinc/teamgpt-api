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
