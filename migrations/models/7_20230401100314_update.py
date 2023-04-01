from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" ADD "GptKeySource" VARCHAR(255);
        CREATE TABLE IF NOT EXISTS "sysgptkey" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "key" VARCHAR(255) NOT NULL,
    "remarks" VARCHAR(255)
);
COMMENT ON COLUMN "organization"."GptKeySource" IS 'SYSTEM: system\nORG: org';;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" DROP COLUMN "GptKeySource";
        DROP TABLE IF EXISTS "sysgptkey";"""
