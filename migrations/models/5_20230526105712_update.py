from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxysubmit" ADD "organization_id" UUID;
        ALTER TABLE "midjourneyproxysubmit" ADD CONSTRAINT "fk_midjourn_organiza_5d8d7de3" FOREIGN KEY ("organization_id") REFERENCES "organization" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxysubmit" DROP CONSTRAINT "fk_midjourn_organiza_5d8d7de3";
        ALTER TABLE "midjourneyproxysubmit" DROP COLUMN "organization_id";"""
