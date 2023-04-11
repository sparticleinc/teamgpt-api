from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "opengptchatmessage" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "model" VARCHAR(100),
    "messages" TEXT,
    "open_gpt_key_id" UUID NOT NULL REFERENCES "opengptkey" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "opengptchatmessage"."model" IS 'GPT3: gpt-3\nGPT3TURBO: gpt-3.5-turbo\nGPT4: gpt-4';;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "opengptchatmessage";"""
