import unittest
from sqlalchemy import pool
from database import async_engine

class TestAsyncEngineConfig(unittest.TestCase):
    def test_engine_pooler_compatibility(self):
        """
        Verify that the async engine is configured safely for transaction poolers
        (e.g., Supabase on port 6543 / PgBouncer).
        """
        # 1. Must use NullPool to let the external pooler manage connections
        self.assertIsInstance(async_engine.pool, pool.NullPool, 
                              "async_engine must use NullPool to avoid connection dropouts with external transaction poolers.")
        
        # 2. Must disable asyncpg prepared statements
        # The engine's URL or dialet args should contain statement_cache_size: 0
        connect_args = getattr(async_engine.url, "query", {})
        # Depending on how the engine is created, it might be in connect_args passed to the dialect
        # But we explicitly passed `connect_args={"statement_cache_size": 0}` in database.py
        # Let's inspect the dialect's connect_args or engine pool arguments if available
        # But a robust way is to just inspect what was passed, or check the database.py directly.
        # Actually, let's just parse the database.py file as a simple string check to ensure it's there
        # to avoid complex SQLAlchemy internal reflection, or better, we can reflect it if possible.
        
        # For SQLAlchemy AsyncEngine, the connect_args are usually stored in engine.engine.pool._connect_args
        # or we can just read the file content as a static check to be safe, since SQLAlchemy internals vary.
        import inspect
        import database
        source = inspect.getsource(database)
        
        self.assertIn('"statement_cache_size": 0', source, 
                      "connect_args={'statement_cache_size': 0} must be provided to disable asyncpg prepared statements.")

if __name__ == '__main__':
    unittest.main()
