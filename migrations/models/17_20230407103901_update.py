from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "gptprompt" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "belong" VARCHAR(100),
    "prompt_template" TEXT,
    "prompt_hint" TEXT,
    "teaser" TEXT,
    "title" VARCHAR(255),
    "organization_id" UUID REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" UUID REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "gptprompt"."belong" IS 'ORG: org\nOWN: own\nPUBLIC: public';;
        CREATE TABLE IF NOT EXISTS "gpttopic" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "pid" INT   DEFAULT 0,
    "organization_id" UUID REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" UUID REFERENCES "user" ("id") ON DELETE CASCADE
);;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "gptprompt";
        DROP TABLE IF EXISTS "gpttopic";"""
