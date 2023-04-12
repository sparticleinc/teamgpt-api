from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "gptchatmessage" ADD "total_tokens" INT;
        ALTER TABLE "gptchatmessage" ADD "prompt_tokens" INT;
        ALTER TABLE "gptchatmessage" ADD "completion_tokens" INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "gptchatmessage" DROP COLUMN "total_tokens";
        ALTER TABLE "gptchatmessage" DROP COLUMN "prompt_tokens";
        ALTER TABLE "gptchatmessage" DROP COLUMN "completion_tokens";"""
