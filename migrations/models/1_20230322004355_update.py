from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "locale" VARCHAR(50);
        ALTER TABLE "user" ADD "nickname" VARCHAR(100);
        ALTER TABLE "user" ALTER COLUMN "email" DROP NOT NULL;
        ALTER TABLE "user" ALTER COLUMN "name" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP COLUMN "locale";
        ALTER TABLE "user" DROP COLUMN "nickname";
        ALTER TABLE "user" ALTER COLUMN "email" SET NOT NULL;
        ALTER TABLE "user" ALTER COLUMN "name" SET NOT NULL;"""
