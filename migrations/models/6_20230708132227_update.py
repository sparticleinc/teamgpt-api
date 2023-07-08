from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conversations" ALTER COLUMN "model" TYPE VARCHAR(100) USING "model"::VARCHAR(100);
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "model" TYPE VARCHAR(100) USING "model"::VARCHAR(100);
        ALTER TABLE "opengptconversations" ALTER COLUMN "model" TYPE VARCHAR(100) USING "model"::VARCHAR(100);
        ALTER TABLE "organization" ADD "gpt_models" JSONB;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" DROP COLUMN "gpt_models";
        ALTER TABLE "conversations" ALTER COLUMN "model" TYPE VARCHAR(100) USING "model"::VARCHAR(100);
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "model" TYPE VARCHAR(100) USING "model"::VARCHAR(100);
        ALTER TABLE "opengptconversations" ALTER COLUMN "model" TYPE VARCHAR(100) USING "model"::VARCHAR(100);"""
