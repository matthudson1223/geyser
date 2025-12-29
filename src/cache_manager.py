"""
Cache Manager for Equity Research Report Generator.

Provides caching functionality for API responses and computed results.
"""

import hashlib
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd
from diskcache import Cache

from .logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Manages caching of data using diskcache."""

    def __init__(self, cache_dir: str = ".cache", enabled: bool = True):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for cache storage
            enabled: Whether caching is enabled
        """
        self.cache_dir = Path(cache_dir)
        self.enabled = enabled
        self.cache: Optional[Cache] = None

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache = Cache(str(self.cache_dir))
            logger.debug(f"Cache initialized at {self.cache_dir}")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from prefix and arguments.

        Args:
            prefix: Key prefix
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key string
        """
        # Create a string representation of args and kwargs
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_string = ":".join(key_parts)

        # Hash for consistent key length
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default value if not found

        Returns:
            Cached value or default
        """
        if not self.enabled or not self.cache:
            return default

        try:
            value = self.cache.get(key, default=default)
            if value is not default:
                logger.debug(f"Cache hit for key: {key}")
            return value
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return default

    def set(
        self, key: str, value: Any, ttl_hours: Optional[float] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_hours: Time to live in hours (None = no expiration)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.cache:
            return False

        try:
            expire = None
            if ttl_hours is not None:
                expire = ttl_hours * 3600  # Convert to seconds

            self.cache.set(key, value, expire=expire)
            logger.debug(f"Cache set for key: {key} (TTL: {ttl_hours}h)")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.cache:
            return False

        try:
            return self.cache.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False

    def clear(self) -> bool:
        """
        Clear all cache.

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.cache:
            return False

        try:
            self.cache.clear()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False

    def cached(
        self,
        prefix: str,
        ttl_hours: Optional[float] = None,
    ):
        """
        Decorator for caching function results.

        Args:
            prefix: Cache key prefix
            ttl_hours: Time to live in hours

        Returns:
            Decorated function
        """

        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)

                # Generate cache key
                cache_key = self._generate_key(prefix, *args, **kwargs)

                # Try to get from cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Using cached result for {func.__name__}")
                    return cached_value

                # Execute function
                logger.debug(f"Cache miss for {func.__name__}, executing...")
                result = func(*args, **kwargs)

                # Store in cache
                self.set(cache_key, result, ttl_hours)

                return result

            return wrapper

        return decorator


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def init_cache(cache_dir: str = ".cache", enabled: bool = True) -> CacheManager:
    """
    Initialize global cache manager.

    Args:
        cache_dir: Directory for cache storage
        enabled: Whether caching is enabled

    Returns:
        CacheManager instance
    """
    global _cache_manager
    _cache_manager = CacheManager(cache_dir, enabled)
    return _cache_manager


def get_cache() -> CacheManager:
    """
    Get global cache manager instance.

    Returns:
        CacheManager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache_dataframe(ticker: str, data_type: str, df: pd.DataFrame, ttl_hours: float = 24) -> None:
    """
    Cache a pandas DataFrame.

    Args:
        ticker: Stock ticker
        data_type: Type of data (e.g., 'historical_prices', 'financials')
        df: DataFrame to cache
        ttl_hours: Time to live in hours
    """
    cache = get_cache()
    key = f"df:{ticker}:{data_type}"
    cache.set(key, df.to_dict(), ttl_hours)


def get_cached_dataframe(ticker: str, data_type: str) -> Optional[pd.DataFrame]:
    """
    Get cached DataFrame.

    Args:
        ticker: Stock ticker
        data_type: Type of data

    Returns:
        DataFrame if found, None otherwise
    """
    cache = get_cache()
    key = f"df:{ticker}:{data_type}"
    data_dict = cache.get(key)

    if data_dict is not None:
        return pd.DataFrame.from_dict(data_dict)
    return None
