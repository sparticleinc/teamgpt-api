from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "gptprompt" ADD "gpt_topic_id" UUID;
        ALTER TABLE "gptprompt" ADD CONSTRAINT "fk_gptpromp_gpttopic_681b4a44" FOREIGN KEY ("gpt_topic_id") REFERENCES "gpttopic" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "gptprompt" DROP CONSTRAINT "fk_gptpromp_gpttopic_681b4a44";
        ALTER TABLE "gptprompt" DROP COLUMN "gpt_topic_id";"""
