from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stripepayments" ADD "email" VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stripepayments" DROP COLUMN "email";"""
