from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" ADD "code" VARCHAR(255);
        ALTER TABLE "organization" ADD "code_expiration_time" TIMESTAMPTZ;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" DROP COLUMN "code";
        ALTER TABLE "organization" DROP COLUMN "code_expiration_time";"""
