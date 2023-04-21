from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stripepayments" ADD "sub_id" VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stripepayments" DROP COLUMN "sub_id";"""
