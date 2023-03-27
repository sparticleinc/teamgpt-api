from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conversations" ADD "model" VARCHAR(100);
        ALTER TABLE "conversationsmessage" ALTER COLUMN "author_user" TYPE VARCHAR(100) USING "author_user"::VARCHAR(100);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conversations" DROP COLUMN "model";
        ALTER TABLE "conversationsmessage" ALTER COLUMN "author_user" TYPE VARCHAR(100) USING "author_user"::VARCHAR(100);"""
