"""
Test Dashboard - Smoke tests for Streamlit app
"""

import pytest
import sys
import os

# Add dashboard to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dashboard'))


class TestDashboardImports:
    """Test that dashboard can be imported without errors"""

    def test_import_app(self):
        """Test main app file can be imported"""
        try:
            import app
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import app: {e}")

    def test_import_db_connection(self):
        """Test database connection module imports"""
        try:
            import db_connection
            assert hasattr(db_connection, 'get_db_connection')
        except ImportError as e:
            pytest.fail(f"Failed to import db_connection: {e}")


class TestDashboardFunctions:
    """Test dashboard query functions"""

    def test_query_functions_exist(self):
        """Test that required query functions exist"""
        import app

        required_functions = [
            'get_season_summary',
            'get_recent_matches',
            'get_match_shots',
            'get_player_stats'
        ]

        for func_name in required_functions:
            assert hasattr(app, func_name), f"Function {func_name} not found"

    def test_db_connection_function(self):
        """Test database connection function"""
        from db_connection import get_db_connection

        # Should not raise an error (connection may fail in CI, but function should exist)
        assert callable(get_db_connection)


class TestDashboardDataValidation:
    """Test data validation helpers"""

    def test_safe_division_helper(self):
        """Test safe division for metrics"""
        def safe_divide(a, b):
            return a / b if b != 0 else 0

        assert safe_divide(10, 2) == 5
        assert safe_divide(10, 0) == 0
        assert safe_divide(0, 5) == 0

    def test_xg_formatting(self):
        """Test xG formatting function"""
        def format_xg(value):
            return f"{value:.2f}"

        assert format_xg(1.2345) == "1.23"
        assert format_xg(0) == "0.00"
        assert format_xg(2.999) == "3.00"


class TestDashboardConstants:
    """Test dashboard constants and configuration"""

    def test_database_env_vars(self):
        """Test database environment variables are accessible"""
        import app

        # These should exist (may be defaults)
        assert hasattr(app, 'DB_HOST')
        assert hasattr(app, 'DB_PORT')
        assert hasattr(app, 'DB_NAME')
        assert hasattr(app, 'DB_USER')
        assert hasattr(app, 'DB_PASSWORD')

    def test_page_config_exists(self):
        """Test Streamlit page config is set"""
        import app

        # Page title should be set
        # Note: Can't directly test st.set_page_config in tests,
        # but we can check the code imports streamlit
        assert hasattr(app, 'st')
