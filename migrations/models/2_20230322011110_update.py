from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "organization" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "name" VARCHAR(100) NOT NULL UNIQUE
);;
        CREATE TABLE IF NOT EXISTS "userorganization" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "organization_id" UUID NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);;
        CREATE TABLE "organization_user" (
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "organization_id" UUID NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "organization_user";
        DROP TABLE IF EXISTS "organization";
        DROP TABLE IF EXISTS "userorganization";"""
