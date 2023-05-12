from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "gptprompt" ADD "zh_CN_prompt_hint" TEXT;
        ALTER TABLE "gptprompt" ADD "zh_CN_prompt_template" TEXT;
        ALTER TABLE "gptprompt" ADD "zh_CN_teaser" TEXT;
        ALTER TABLE "gptprompt" ADD "zh_CN_title" VARCHAR(255);
        CREATE TABLE IF NOT EXISTS "midjourneyproxyhook" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "run_id" VARCHAR(255),
    "action" VARCHAR(255),
    "prompt" VARCHAR(255),
    "promptEn" VARCHAR(255),
    "description" VARCHAR(255),
    "state" VARCHAR(255),
    "submitTime" VARCHAR(255),
    "finishTime" VARCHAR(255),
    "imageUrl" VARCHAR(255),
    "status" VARCHAR(255),
    "midjourney_proxy_submit_id" UUID REFERENCES "midjourneyproxysubmit" ("id") ON DELETE CASCADE
);;
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
    "notifyHook" VARCHAR(255),
    "req_code" INT,
    "req_description" VARCHAR(255),
    "req_result" VARCHAR(255),
    "status" VARCHAR(255)   DEFAULT 'IN_PROGRESS',
    "image_url" VARCHAR(255),
    "finish_time" VARCHAR(255),
    "user_id" UUID REFERENCES "user" ("id") ON DELETE CASCADE
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
        ALTER TABLE "stripeproducts" ADD "product" VARCHAR(255);"""
