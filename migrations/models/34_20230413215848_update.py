from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" ADD "user" VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" DROP COLUMN "user";"""
