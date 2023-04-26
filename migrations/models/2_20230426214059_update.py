from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stripeproducts" DROP COLUMN "set_month";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stripeproducts" ADD "set_month" INT   DEFAULT 0;"""
