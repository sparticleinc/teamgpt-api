from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "systemconfig" ALTER COLUMN "value" TYPE JSONB USING "value"::JSONB;
        ALTER TABLE "systemconfig" ALTER COLUMN "value" TYPE JSONB USING "value"::JSONB;
        ALTER TABLE "systemconfig" ALTER COLUMN "value" TYPE JSONB USING "value"::JSONB;
        ALTER TABLE "systemconfig" ALTER COLUMN "value" TYPE JSONB USING "value"::JSONB;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "systemconfig" ALTER COLUMN "value" TYPE TEXT USING "value"::TEXT;
        ALTER TABLE "systemconfig" ALTER COLUMN "value" TYPE TEXT USING "value"::TEXT;
        ALTER TABLE "systemconfig" ALTER COLUMN "value" TYPE TEXT USING "value"::TEXT;
        ALTER TABLE "systemconfig" ALTER COLUMN "value" TYPE TEXT USING "value"::TEXT;"""
