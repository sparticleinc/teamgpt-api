from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conversationsmessage" ADD "model" VARCHAR(100);
        ALTER TABLE "organization" ALTER COLUMN "gpt_models" DROP DEFAULT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" ALTER COLUMN "gpt_models" SET;
        ALTER TABLE "conversationsmessage" DROP COLUMN "model";"""
