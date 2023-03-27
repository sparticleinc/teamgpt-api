from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conversations" ALTER COLUMN "model" TYPE VARCHAR(100) USING "model"::VARCHAR(100);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conversations" ALTER COLUMN "model" TYPE VARCHAR(100) USING "model"::VARCHAR(100);"""
