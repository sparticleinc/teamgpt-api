from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxysubmit" ALTER COLUMN "prompt" TYPE TEXT USING "prompt"::TEXT;
        ALTER TABLE "midjourneyproxysubmit" ALTER COLUMN "prompt" TYPE TEXT USING "prompt"::TEXT;
        ALTER TABLE "midjourneyproxysubmit" ALTER COLUMN "prompt" TYPE TEXT USING "prompt"::TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "midjourneyproxysubmit" ALTER COLUMN "prompt" TYPE VARCHAR(50) USING "prompt"::VARCHAR(50);
        ALTER TABLE "midjourneyproxysubmit" ALTER COLUMN "prompt" TYPE VARCHAR(50) USING "prompt"::VARCHAR(50);
        ALTER TABLE "midjourneyproxysubmit" ALTER COLUMN "prompt" TYPE VARCHAR(50) USING "prompt"::VARCHAR(50);"""
