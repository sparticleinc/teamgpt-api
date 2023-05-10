from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "midjourneyproxyhook" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "req_msg" JSONB,
    "run_id" VARCHAR(255),
    "action" VARCHAR(255),
    "prompt" VARCHAR(255),
    "promptEn" VARCHAR(255),
    "description" VARCHAR(255),
    "state" VARCHAR(255),
    "submitTime" VARCHAR(255),
    "finishTime" VARCHAR(255),
    "imageUrl" VARCHAR(255),
    "status" VARCHAR(255)
);;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "midjourneyproxyhook";"""
