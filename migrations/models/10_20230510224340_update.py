from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxysubmit" ADD "req_description" VARCHAR(255);
        ALTER TABLE "midjourneyproxysubmit" ADD "req_code" INT;
        ALTER TABLE "midjourneyproxysubmit" ADD "req_result" VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxysubmit" DROP COLUMN "req_description";
        ALTER TABLE "midjourneyproxysubmit" DROP COLUMN "req_code";
        ALTER TABLE "midjourneyproxysubmit" DROP COLUMN "req_result";"""
