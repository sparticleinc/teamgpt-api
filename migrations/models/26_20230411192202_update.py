from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "messages" TYPE JSONB USING "messages"::JSONB;
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "messages" TYPE JSONB USING "messages"::JSONB;
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "messages" TYPE JSONB USING "messages"::JSONB;
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "messages" TYPE JSONB USING "messages"::JSONB;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "messages" TYPE TEXT USING "messages"::TEXT;
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "messages" TYPE TEXT USING "messages"::TEXT;
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "messages" TYPE TEXT USING "messages"::TEXT;
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "messages" TYPE TEXT USING "messages"::TEXT;"""
