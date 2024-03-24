from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conversationsmessage" ADD "privacy_chat_sta" BOOL   DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conversationsmessage" DROP COLUMN "privacy_chat_sta";"""
