from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "opengptkey" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "key" VARCHAR(255) NOT NULL,
    "gpt_key" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "opengptchatmessage" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "model" VARCHAR(100),
    "temperature" INT,
    "top_p" INT,
    "n" INT,
    "stream" BOOL,
    "stop" VARCHAR(100),
    "max_tokens" INT,
    "presence_penalty" INT,
    "frequency_penalty" INT,
    "messages" JSONB,
    "req_message" TEXT,
    "run_time" INT,
    "prompt_tokens" INT,
    "completion_tokens" INT,
    "total_tokens" INT,
    "logit_bias" JSONB,
    "user" VARCHAR(255),
    "open_gpt_key_id" UUID NOT NULL REFERENCES "opengptkey" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "opengptchatmessage"."model" IS 'GPT3: gpt-3\nGPT3TURBO: gpt-3.5-turbo\nGPT4: gpt-4';
CREATE TABLE IF NOT EXISTS "opengptconversations" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "title" VARCHAR(255) NOT NULL,
    "model" VARCHAR(100),
    "open_gpt_key_id" UUID NOT NULL REFERENCES "opengptkey" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "opengptconversations"."model" IS 'GPT3: gpt-3\nGPT3TURBO: gpt-3.5-turbo\nGPT4: gpt-4';
CREATE TABLE IF NOT EXISTS "opengptconversationsmessage" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "message" TEXT,
    "content_type" VARCHAR(100),
    "author_user" VARCHAR(100),
    "run_time" INT,
    "open_gpt_key_id" UUID NOT NULL REFERENCES "opengptkey" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "opengptconversationsmessage"."content_type" IS 'TEXT: text\nIMAGE: image\nAUDIO: audio\nVIDEO: video';
COMMENT ON COLUMN "opengptconversationsmessage"."author_user" IS 'USER: user\nSYSTEM: system\nASSISTANT: assistant';
CREATE TABLE IF NOT EXISTS "stripeproducts" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "name" VARCHAR(255),
    "max_number" INT   DEFAULT 0,
    "max_tokens" INT   DEFAULT 0,
    "sys_token" BOOL   DEFAULT False,
    "api_id" VARCHAR(255),
    "order" INT   DEFAULT 0,
    "month" INT   DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "stripewebhooklog" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "type" VARCHAR(255),
    "data" JSONB,
    "run_sta" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "sysgptkey" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "key" VARCHAR(255) NOT NULL,
    "remarks" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "user_id" VARCHAR(100) NOT NULL UNIQUE,
    "email" VARCHAR(100),
    "name" VARCHAR(100),
    "picture" VARCHAR(255),
    "locale" VARCHAR(50),
    "nickname" VARCHAR(100),
    "current_organization" VARCHAR(100),
    "super" BOOL   DEFAULT False
);
CREATE TABLE IF NOT EXISTS "organization" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "name" VARCHAR(100) NOT NULL UNIQUE,
    "picture" VARCHAR(255),
    "gpt_key_source" VARCHAR(255),
    "code" VARCHAR(255),
    "code_expiration_time" TIMESTAMPTZ,
    "super" BOOL   DEFAULT False,
    "creator_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aicharacter" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "instruction" TEXT,
    "organization_id" UUID NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "conversations" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "title" VARCHAR(255) NOT NULL,
    "model" VARCHAR(100),
    "organization_id" UUID NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "conversations"."model" IS 'GPT3: gpt-3\nGPT3TURBO: gpt-3.5-turbo\nGPT4: gpt-4';
CREATE TABLE IF NOT EXISTS "conversationsmessage" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "message" TEXT,
    "shown_message" TEXT,
    "content_type" VARCHAR(100),
    "author_user" VARCHAR(100),
    "run_time" INT,
    "key" VARCHAR(255),
    "prompt_tokens" INT,
    "completion_tokens" INT,
    "total_tokens" INT,
    "conversation_id" UUID NOT NULL REFERENCES "conversations" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "conversationsmessage"."content_type" IS 'TEXT: text\nIMAGE: image\nAUDIO: audio\nVIDEO: video';
COMMENT ON COLUMN "conversationsmessage"."author_user" IS 'USER: user\nSYSTEM: system\nASSISTANT: assistant';
CREATE TABLE IF NOT EXISTS "gptkey" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "key" VARCHAR(255) NOT NULL,
    "organization_id" UUID NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "gptchatmessage" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "in_message" TEXT,
    "out_message" TEXT,
    "token_num" INT   DEFAULT 0,
    "key" VARCHAR(255),
    "prompt_tokens" INT,
    "completion_tokens" INT,
    "total_tokens" INT,
    "conversation_id" UUID NOT NULL REFERENCES "conversations" ("id") ON DELETE CASCADE,
    "organization_id" UUID NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "gpttopic" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "pid" UUID,
    "organization_id" UUID REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" UUID REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "gptprompt" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "belong" JSONB,
    "prompt_template" TEXT,
    "prompt_hint" TEXT,
    "teaser" TEXT,
    "title" VARCHAR(255),
    "gpt_topic_id" UUID REFERENCES "gpttopic" ("id") ON DELETE CASCADE,
    "organization_id" UUID REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" UUID REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "stripepayments" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "api_id" VARCHAR(255),
    "sub_id" VARCHAR(255),
    "type" VARCHAR(255),
    "invoice" VARCHAR(255),
    "customer_details" JSONB,
    "organization_id" UUID REFERENCES "organization" ("id") ON DELETE CASCADE,
    "stripe_products_id" UUID REFERENCES "stripeproducts" ("id") ON DELETE CASCADE,
    "user_id" UUID REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "userorganization" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "role" VARCHAR(100),
    "organization_id" UUID NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "userorganization"."role" IS 'CREATOR: creator\nMEMBER: member';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "organization_user" (
    "organization_id" UUID NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
