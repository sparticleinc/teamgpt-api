from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" ADD "logit_bias" JSONB;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" DROP COLUMN "logit_bias";"""
