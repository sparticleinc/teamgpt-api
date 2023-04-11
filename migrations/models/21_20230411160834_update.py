from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "opengptconversations" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "title" VARCHAR(255) NOT NULL,
    "model" VARCHAR(100)
);
COMMENT ON COLUMN "opengptconversations"."model" IS 'GPT3: gpt-3\nGPT3TURBO: gpt-3.5-turbo\nGPT4: gpt-4';;
        CREATE TABLE IF NOT EXISTS "opengptconversationsmessage" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "message" TEXT,
    "content_type" VARCHAR(100),
    "author_user" VARCHAR(100),
    "run_time" INT
);
COMMENT ON COLUMN "opengptconversationsmessage"."content_type" IS 'TEXT: text\nIMAGE: image\nAUDIO: audio\nVIDEO: video';
COMMENT ON COLUMN "opengptconversationsmessage"."author_user" IS 'USER: user\nSYSTEM: system\nASSISTANT: assistant';;
        CREATE TABLE IF NOT EXISTS "opengptkey" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "key" VARCHAR(255) NOT NULL,
    "gpt_key" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255)
);;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "opengptconversations";
        DROP TABLE IF EXISTS "opengptconversationsmessage";
        DROP TABLE IF EXISTS "opengptkey";"""
