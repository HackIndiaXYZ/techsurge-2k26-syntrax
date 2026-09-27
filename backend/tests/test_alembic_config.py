import os
import sys
import unittest
from alembic.config import Config

class TestAlembicConfig(unittest.TestCase):
    def test_database_url_interpolation(self):
        """
        Verify that a database URL containing percent-encoded characters (like %20)
        does not cause ConfigParser interpolation errors when set in Alembic config.
        """
        # Create a basic alembic config
        config = Config()
        
        # Simulated database URL with a percent-encoded character (%20 for space)
        # We do NOT use real credentials here.
        simulated_url = "postgresql+asyncpg://user:password%20encoded@host:5432/postgres"
        
        # Apply the same fix used in env.py
        safe_db_url = simulated_url.replace("%", "%%")
        
        # Set the option in Alembic config
        config.set_main_option("sqlalchemy.url", safe_db_url)
        
        # Retrieve the option. This will trigger interpolation if present.
        retrieved_url = config.get_main_option("sqlalchemy.url")
        
        # Verify it matches the original URL (ConfigParser un-escapes %% to %)
        self.assertEqual(retrieved_url, simulated_url)

if __name__ == '__main__':
    unittest.main()
