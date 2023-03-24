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
