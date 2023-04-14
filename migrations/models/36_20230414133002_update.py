from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "gptprompt" RENAME COLUMN "Belong" TO "belong";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "gptprompt" RENAME COLUMN "belong" TO "Belong";"""
