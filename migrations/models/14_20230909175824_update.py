from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "maskcontent" ADD "masked_content" VARCHAR(255);
        ALTER TABLE "maskcontent" ADD "masked_result" VARCHAR(255);
        ALTER TABLE "maskcontent" ADD "privacy_detected" BOOL   DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "maskcontent" DROP COLUMN "masked_content";
        ALTER TABLE "maskcontent" DROP COLUMN "masked_result";
        ALTER TABLE "maskcontent" DROP COLUMN "privacy_detected";"""
