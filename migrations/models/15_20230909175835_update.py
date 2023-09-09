from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "maskcontent" DROP COLUMN "mask_content";
        ALTER TABLE "maskcontent" DROP COLUMN "mask_result";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "maskcontent" ADD "mask_content" VARCHAR(255);
        ALTER TABLE "maskcontent" ADD "mask_result" VARCHAR(255);"""
