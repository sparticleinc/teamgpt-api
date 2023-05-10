from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxyhook" ALTER COLUMN "midjourney_proxy_submit_id" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxyhook" ALTER COLUMN "midjourney_proxy_submit_id" SET NOT NULL;"""
