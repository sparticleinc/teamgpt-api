from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" DROP COLUMN "token";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" ADD "token" INT;"""
