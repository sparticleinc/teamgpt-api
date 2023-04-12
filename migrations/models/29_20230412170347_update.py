from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" ADD "total_tokens" INT;
        ALTER TABLE "opengptchatmessage" ADD "prompt_tokens" INT;
        ALTER TABLE "opengptchatmessage" ADD "completion_tokens" INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" DROP COLUMN "total_tokens";
        ALTER TABLE "opengptchatmessage" DROP COLUMN "prompt_tokens";
        ALTER TABLE "opengptchatmessage" DROP COLUMN "completion_tokens";"""
