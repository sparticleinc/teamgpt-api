from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxysubmituv" ADD "req_code" INT;
        CREATE TABLE IF NOT EXISTS "userattribute" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "title" VARCHAR(255),
    "value" VARCHAR(255),
    "answer" VARCHAR(255),
    "user_id" UUID REFERENCES "user" ("id") ON DELETE CASCADE
);;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxysubmituv" DROP COLUMN "req_code";
        DROP TABLE IF EXISTS "userattribute";"""
