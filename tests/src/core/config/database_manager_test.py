import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.config import create_database_manager


async def test_basic_connection():
    print(f"🔍 Database Connection Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 Test User: Gordon")
    print("=" * 50)

    try:
        db_manager = create_database_manager()
        print("✅ Database manager created successfully")

        connection_result = await db_manager.connect()
        if connection_result:
            print("✅ Database connection successful")
            health_info = await db_manager.health_check()
            print(f"📊 Health Status: {health_info}")
        else:
            print("❌ Database connection failed")

        await db_manager.disconnect()
        print("🔌 Database connection closed")

    except Exception as e:
        print(f"💥 Error: {e}")


async def test_context_manager():
    print("\n📝 Context Manager Test...")

    try:
        async with create_database_manager() as db_manager:
            print("✅ Database auto-connected successfully")

            async with db_manager.get_session() as session:
                from sqlalchemy import text
                result = await session.execute(text("SELECT 'Hello Nuwa!' as message"))
                message = result.scalar()
                print(f"🔍 Query Result: {message}")

        print("🔌 Database auto-disconnected")

    except Exception as e:
        print(f"💥 Error: {e}")


async def test_memory_database():
    print("\n🧠 In-Memory Database Test...")

    try:
        memory_db_url = "sqlite+aiosqlite:///:memory:"

        async with create_database_manager(memory_db_url) as db:
            print("✅ In-memory database connected successfully")

            async with db.get_session() as session:
                from sqlalchemy import text

                await session.execute(text("""
                                           CREATE TABLE users
                                           (
                                               id    INTEGER PRIMARY KEY,
                                               name  TEXT,
                                               email TEXT
                                           )
                                           """))

                await session.execute(text("""
                                           INSERT INTO users (name, email)
                                           VALUES ('Alice', 'alice@nuwa.com'),
                                                  ('Bob', 'bob@nuwa.com')
                                           """))

                result = await session.execute(text("SELECT name, email FROM users"))
                users = result.fetchall()

                print("📋 User List:")
                for user in users:
                    print(f"   - {user.name}: {user.email}")

    except Exception as e:
        print(f"💥 Error: {e}")


async def main():
    print("🚀 Database Testing")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 Gordon")
    print("=" * 40)

    await test_basic_connection()
    await test_context_manager()
    await test_memory_database()

    print("\n" + "=" * 40)
    print("🎉 Testing Complete!")


if __name__ == '__main__':
    asyncio.run(main())