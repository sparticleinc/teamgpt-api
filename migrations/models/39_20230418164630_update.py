from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "paidpackages" ADD "webhook_type" VARCHAR(255);
        ALTER TABLE "paidpackages" ALTER COLUMN "organization_id" DROP NOT NULL;
        ALTER TABLE "paidpackages" ALTER COLUMN "user_id" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "paidpackages" DROP COLUMN "webhook_type";
        ALTER TABLE "paidpackages" ALTER COLUMN "organization_id" SET NOT NULL;
        ALTER TABLE "paidpackages" ALTER COLUMN "user_id" SET NOT NULL;"""
