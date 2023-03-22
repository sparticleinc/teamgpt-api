from enum import Enum


class Role(str, Enum):
    CREATOR = 'creator'
    MEMBER = 'member'
