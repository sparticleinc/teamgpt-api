from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stripeproducts" ADD "mode" VARCHAR(12)   DEFAULT 'subscription';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stripeproducts" DROP COLUMN "mode";"""
