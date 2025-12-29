"""
Tests for cache manager.
"""

import pytest
from src.cache_manager import CacheManager


class TestCacheManager:
    """Tests for CacheManager class."""

    def test_cache_initialization(self, tmp_path):
        """Test cache initialization."""
        cache_dir = tmp_path / ".cache"
        cache = CacheManager(cache_dir=str(cache_dir), enabled=True)

        assert cache.enabled is True
        assert cache.cache_dir == cache_dir
        assert cache.cache is not None

    def test_cache_disabled(self):
        """Test cache with disabled state."""
        cache = CacheManager(enabled=False)

        assert cache.enabled is False
        assert cache.get("test") is None
        assert cache.set("test", "value") is False

    def test_cache_set_and_get(self, mock_cache):
        """Test setting and getting values."""
        assert mock_cache.set("test_key", "test_value") is True
        assert mock_cache.get("test_key") == "test_value"

    def test_cache_get_default(self, mock_cache):
        """Test getting with default value."""
        assert mock_cache.get("nonexistent", default="default") == "default"

    def test_cache_delete(self, mock_cache):
        """Test deleting cached values."""
        mock_cache.set("test_key", "test_value")
        assert mock_cache.get("test_key") == "test_value"

        mock_cache.delete("test_key")
        assert mock_cache.get("test_key") is None

    def test_cache_clear(self, mock_cache):
        """Test clearing all cache."""
        mock_cache.set("key1", "value1")
        mock_cache.set("key2", "value2")

        assert mock_cache.clear() is True
        assert mock_cache.get("key1") is None
        assert mock_cache.get("key2") is None

    def test_cache_with_ttl(self, mock_cache):
        """Test cache with TTL (basic test)."""
        # Note: Testing actual expiration would require time.sleep()
        # which makes tests slow. This just tests the API.
        assert mock_cache.set("test_key", "test_value", ttl_hours=1) is True
        assert mock_cache.get("test_key") == "test_value"

    def test_cache_decorator(self, mock_cache):
        """Test cache decorator."""
        call_count = [0]

        @mock_cache.cached("test_func", ttl_hours=1)
        def expensive_function(x):
            call_count[0] += 1
            return x * 2

        # First call should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count[0] == 1

        # Second call should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count[0] == 1  # Not incremented
