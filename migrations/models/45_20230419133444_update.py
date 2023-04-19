from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "stripepayments" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "api_id" VARCHAR(255),
    "type" VARCHAR(255),
    "organization_id" UUID REFERENCES "organization" ("id") ON DELETE CASCADE,
    "stripe_products_id" UUID REFERENCES "stripeproducts" ("id") ON DELETE CASCADE,
    "user_id" UUID REFERENCES "user" ("id") ON DELETE CASCADE
);;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "stripepayments";"""
