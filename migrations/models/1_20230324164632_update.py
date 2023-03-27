from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "conversations" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "title" VARCHAR(255) NOT NULL,
    "organization_id" UUID NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);;
        CREATE TABLE IF NOT EXISTS "conversationsmessage" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "message" TEXT,
    "content_type" VARCHAR(100),
    "author_user" VARCHAR(100),
    "conversation_id" UUID NOT NULL REFERENCES "conversations" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "conversationsmessage"."content_type" IS 'TEXT: text\nIMAGE: image\nAUDIO: audio\nVIDEO: video';
COMMENT ON COLUMN "conversationsmessage"."author_user" IS 'USER: user\nSYSTEM: system';;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "conversations";
        DROP TABLE IF EXISTS "conversationsmessage";"""
