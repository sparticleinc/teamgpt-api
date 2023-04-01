from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" RENAME COLUMN "GptKeySource" TO "gpt_key_source";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" RENAME COLUMN "gpt_key_source" TO "GptKeySource";"""
