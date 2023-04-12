from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conversationsmessage" ADD "total_tokens" INT;
        ALTER TABLE "conversationsmessage" ADD "prompt_tokens" INT;
        ALTER TABLE "conversationsmessage" ADD "completion_tokens" INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conversationsmessage" DROP COLUMN "total_tokens";
        ALTER TABLE "conversationsmessage" DROP COLUMN "prompt_tokens";
        ALTER TABLE "conversationsmessage" DROP COLUMN "completion_tokens";"""
