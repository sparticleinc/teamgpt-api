from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxysubmit" ADD "user_id" UUID;
        ALTER TABLE "midjourneyproxysubmit" ADD CONSTRAINT "fk_midjourn_user_df415d67" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxysubmit" DROP CONSTRAINT "fk_midjourn_user_df415d67";
        ALTER TABLE "midjourneyproxysubmit" DROP COLUMN "user_id";"""
