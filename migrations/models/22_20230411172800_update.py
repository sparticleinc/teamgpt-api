from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptconversations" ADD "open_gpt_key_id" UUID NOT NULL;
        ALTER TABLE "opengptconversationsmessage" ADD "open_gpt_key_id" UUID NOT NULL;
        ALTER TABLE "opengptconversations" ADD CONSTRAINT "fk_opengptc_opengptk_8145796c" FOREIGN KEY ("open_gpt_key_id") REFERENCES "opengptkey" ("id") ON DELETE CASCADE;
        ALTER TABLE "opengptconversationsmessage" ADD CONSTRAINT "fk_opengptc_opengptk_fd70f113" FOREIGN KEY ("open_gpt_key_id") REFERENCES "opengptkey" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptconversationsmessage" DROP CONSTRAINT "fk_opengptc_opengptk_fd70f113";
        ALTER TABLE "opengptconversations" DROP CONSTRAINT "fk_opengptc_opengptk_8145796c";
        ALTER TABLE "opengptconversations" DROP COLUMN "open_gpt_key_id";
        ALTER TABLE "opengptconversationsmessage" DROP COLUMN "open_gpt_key_id";"""
