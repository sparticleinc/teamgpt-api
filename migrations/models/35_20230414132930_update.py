from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "gptprompt" ADD "Belong" JSONB;
        ALTER TABLE "gptprompt" DROP COLUMN "belong";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "gptprompt" ADD "belong" VARCHAR(100);
        ALTER TABLE "gptprompt" DROP COLUMN "Belong";"""
