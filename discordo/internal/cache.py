"""Cache for mention completion to avoid redundant gateway requests."""

from typing import Dict, Optional
import threading


class Cache:
    """
    Thread-safe cache for caching search results.
    
    Used for mention completion to prevent overwhelming the gateway
    with redundant search requests.
    """
    
    def __init__(self):
        """Initialize the cache."""
        self._items: Dict[str, int] = {}
        self._lock = threading.RLock()
    
    def create(self, query: str, value: int) -> None:
        """
        Store a value in the cache.
        
        Args:
            query: The cache key (search query)
            value: The count value to cache
        """
        with self._lock:
            self._items[query] = value
    
    def exists(self, query: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            query: The cache key
            
        Returns:
            True if the key exists, False otherwise
        """
        with self._lock:
            return query in self._items
    
    def get(self, query: str) -> Optional[int]:
        """
        Retrieve a value from the cache.
        
        Args:
            query: The cache key
            
        Returns:
            The cached value or None if not found
        """
        with self._lock:
            return self._items.get(query)
    
    def invalidate(self, name: str, limit: int) -> None:
        """
        Invalidate cache entries for a given name prefix.
        
        This is used when a member leaves and the search query reaches
        the search limit. For example, if we've searched for "aa", "ab",
        "ac", ..., "ay" (reaching the limit), and "ay" leaves, then
        searching for "az" won't work because it's not in the results.
        
        So we invalidate all prefixes of the leaving member's name that
        reached the search limit.
        
        Args:
            name: The member name (e.g., "alice" or "alice_123")
            limit: The search limit (when we've cached results)
        """
        with self._lock:
            while name:
                if name in self._items and self._items[name] >= limit:
                    # Delete all prefixes of this name
                    while name:
                        self._items.pop(name, None)
                        name = name[:-1]
                else:
                    # Move to next prefix
                    name = name[:-1]
