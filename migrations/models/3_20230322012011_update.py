from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" ADD "creator_id" UUID NOT NULL;
        ALTER TABLE "organization" ADD "picture" VARCHAR(255);
        ALTER TABLE "organization" ADD CONSTRAINT "fk_organiza_user_b31c5200" FOREIGN KEY ("creator_id") REFERENCES "user" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" DROP CONSTRAINT "fk_organiza_user_b31c5200";
        ALTER TABLE "organization" DROP COLUMN "creator_id";
        ALTER TABLE "organization" DROP COLUMN "picture";"""
