from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" ADD "frequency_penalty" INT;
        ALTER TABLE "opengptchatmessage" ADD "max_tokens" INT;
        ALTER TABLE "opengptchatmessage" ADD "presence_penalty" INT;
        ALTER TABLE "opengptchatmessage" ADD "n" INT;
        ALTER TABLE "opengptchatmessage" ADD "temperature" INT;
        ALTER TABLE "opengptchatmessage" ADD "stream" BOOL;
        ALTER TABLE "opengptchatmessage" ADD "stop" VARCHAR(100);
        ALTER TABLE "opengptchatmessage" ADD "top_p" INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "opengptchatmessage" DROP COLUMN "frequency_penalty";
        ALTER TABLE "opengptchatmessage" DROP COLUMN "max_tokens";
        ALTER TABLE "opengptchatmessage" DROP COLUMN "presence_penalty";
        ALTER TABLE "opengptchatmessage" DROP COLUMN "n";
        ALTER TABLE "opengptchatmessage" DROP COLUMN "temperature";
        ALTER TABLE "opengptchatmessage" DROP COLUMN "stream";
        ALTER TABLE "opengptchatmessage" DROP COLUMN "stop";
        ALTER TABLE "opengptchatmessage" DROP COLUMN "top_p";"""
