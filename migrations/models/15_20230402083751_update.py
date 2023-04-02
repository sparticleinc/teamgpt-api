from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" ALTER COLUMN "gpt_key_source" TYPE VARCHAR(255) USING "gpt_key_source"::VARCHAR(255);
        ALTER TABLE "organization" ALTER COLUMN "gpt_key_source" TYPE VARCHAR(255) USING "gpt_key_source"::VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" ALTER COLUMN "gpt_key_source" TYPE VARCHAR(255) USING "gpt_key_source"::VARCHAR(255);
        ALTER TABLE "organization" ALTER COLUMN "gpt_key_source" TYPE VARCHAR(255) USING "gpt_key_source"::VARCHAR(255);"""
