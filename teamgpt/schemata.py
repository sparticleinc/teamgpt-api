from tortoise.contrib.pydantic import pydantic_model_creator
from teamgpt import models

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
)
