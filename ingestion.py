from chat.document_index import build_index
from database.base import get_db

import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    async for db in get_db():
        retriever = await build_index(db)
        print("Index built and loaded successfully.")

if __name__ == "__main__":
    
    asyncio.run(main())