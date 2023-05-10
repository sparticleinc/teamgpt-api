from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxyhook" ADD "midjourney_proxy_submit_id" UUID NOT NULL;
        CREATE TABLE IF NOT EXISTS "midjourneyproxysubmit" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "action" VARCHAR(50),
    "prompt" VARCHAR(50),
    "taskId" VARCHAR(255),
    "index" INT,
    "state" VARCHAR(50),
    "notifyHook" VARCHAR(255)
);;
        CREATE TABLE IF NOT EXISTS "midjourneyproxysubmituv" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "state" VARCHAR(50),
    "content" VARCHAR(50),
    "notifyHook" VARCHAR(255)
);;
        ALTER TABLE "midjourneyproxyhook" ADD CONSTRAINT "fk_midjourn_midjourn_cb640354" FOREIGN KEY ("midjourney_proxy_submit_id") REFERENCES "midjourneyproxysubmit" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxyhook" DROP CONSTRAINT "fk_midjourn_midjourn_cb640354";
        ALTER TABLE "midjourneyproxyhook" DROP COLUMN "midjourney_proxy_submit_id";
        DROP TABLE IF EXISTS "midjourneyproxysubmit";
        DROP TABLE IF EXISTS "midjourneyproxysubmituv";"""
