from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conversationsmessage" DROP COLUMN "token_num";
        ALTER TABLE "gptchatmessage" ADD "conversation_id" UUID NOT NULL;
        ALTER TABLE "gptchatmessage" ADD CONSTRAINT "fk_gptchatm_conversa_ea2b1b16" FOREIGN KEY ("conversation_id") REFERENCES "conversations" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "gptchatmessage" DROP CONSTRAINT "fk_gptchatm_conversa_ea2b1b16";
        ALTER TABLE "gptchatmessage" DROP COLUMN "conversation_id";
        ALTER TABLE "conversationsmessage" ADD "token_num" INT   DEFAULT 0;"""
