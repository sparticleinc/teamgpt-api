from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" DROP COLUMN "functions_call";
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "functions" TYPE JSONB USING "functions"::JSONB;
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "functions" TYPE JSONB USING "functions"::JSONB;
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "functions" TYPE JSONB USING "functions"::JSONB;
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "functions" TYPE JSONB USING "functions"::JSONB;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" ADD "functions_call" JSONB;
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "functions" TYPE VARCHAR(255) USING "functions"::VARCHAR(255);
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "functions" TYPE VARCHAR(255) USING "functions"::VARCHAR(255);
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "functions" TYPE VARCHAR(255) USING "functions"::VARCHAR(255);
        ALTER TABLE "opengptchatmessage" ALTER COLUMN "functions" TYPE VARCHAR(255) USING "functions"::VARCHAR(255);"""
