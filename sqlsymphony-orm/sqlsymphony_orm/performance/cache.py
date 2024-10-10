import time
from functools import wraps
from typing import Callable, Type, Any
from sqlsymphony_orm.patterns import Singleton


class CacheBase(object):
	"""
	An abstract base class for implementing a cache.

	This class defines the basic interface for a cache, including methods for
	getting, setting, and clearing cache entries.
	"""

	def get(self, key: str) -> Any:
		"""
		Retrieve a value from the cache.

		Args: key (str): The key to retrieve.

		Returns: Any: The cached value, or None if the key is not found.

		:param		key:  The key
		:type		key:  str

		:returns:	{ description_of_the_return_value }
		:rtype:		Any
		"""
		raise NotImplementedError

	def set(self, key: str, value: Any, timestamp: float) -> None:
		"""
		Store a value in the cache.

		Args: key (str): The key to store the value under. value (Any): The
		value to store. timestamp (float): The timestamp when the value was
		generated.

		:param		key:		The new value
		:type		key:		str
		:param		value:		The value
		:type		value:		Any
		:param		timestamp:	The timestamp
		:type		timestamp:	float

		:returns:	{ description_of_the_return_value }
		:rtype:		None
		"""
		raise NotImplementedError

	def clear(self) -> None:
		"""
		Clear all entries from the cache.
		"""
		raise NotImplementedError


class InMemoryCache(CacheBase):
	"""
	An in-memory cache implementation.

	This class stores cached values in a dictionary, with a separate dictionary
	to track the access times of each entry. Entries are evicted from the cache
	when the maximum size is reached or when the time-to-live (TTL) has expired.
	"""

	def __init__(self, max_size: int = 1000, ttl: int = 60) -> None:
		self.max_size = max_size
		self.ttl = ttl
		self.cache = {}
		self.timestamps = {}

	def get(self, key: str) -> Any:
		if key in self.cache:
			if time.time() - self.timestamps[key] <= self.ttl:
				return self.cache[key]
			else:
				del self.cache[key]
				del self.timestamps[key]
		return None

	def set(self, key: str, value: Any, timestamp: float) -> None:
		if len(self.cache) >= self.max_size:
			oldest_key = min(self.timestamps, key=self.timestamps.get)
			del self.cache[oldest_key]
			del self.timestamps[oldest_key]
		self.cache[key] = value
		self.timestamps[key] = timestamp

	def clear(self) -> None:
		self.cache.clear()
		self.timestamps.clear()


class CacheFactory(object):
	"""
	A factory for creating different types of caches.

	This class follows the Factory pattern to provide a consistent interface for
	creating cache instances, without exposing the specific implementation details.
	"""

	@staticmethod
	def create_cache(cache_type: Type[CacheBase], *args, **kwargs) -> CacheBase:
		"""
		Create a new cache instance of the specified type.

		Args: cache_type (Type[CacheBase]): The type of cache to create. *args:
		Positional arguments to pass to the cache constructor. **kwargs: Keyword
		arguments to pass to the cache constructor.

		Returns: CacheBase: A new instance of the specified cache type.

		:param		cache_type:	 The cache type
		:type		cache_type:	 { type_description }
		:param		args:		 The arguments
		:type		args:		 list
		:param		kwargs:		 The keywords arguments
		:type		kwargs:		 dictionary

		:returns:	The cache base.
		:rtype:		CacheBase
		"""
		return cache_type(*args, **kwargs)


class SingletonCache(CacheBase, metaclass=Singleton):
	"""

	A Singleton cache that delegates to a specific cache implementation.

	This class follows the Singleton pattern to ensure that there is only one
	instance of the cache in the application. It also uses the Factory pattern
	to create the underlying cache implementation.
	"""

	def __init__(self, cache_type: Type[CacheBase], *args, **kwargs) -> None:
		self.cache = CacheFactory.create_cache(cache_type, *args, **kwargs)

	def get(self, key: str) -> Any:
		return self.cache.get(key)

	def set(self, key: str, value: Any, timestamp: float) -> None:
		self.cache.set(key, value, timestamp)

	def clear(self) -> None:
		self.cache.clear()


def cached(
	cache: SingletonCache,
	key_func: Callable[[Any, Any], str] = lambda *args, **kwargs: str(args)
	+ str(kwargs),
) -> Callable:
	"""
	A decorator that caches the results of a function or method.

	This decorator uses the provided cache instance to store and retrieve the
	results of the decorated function or method. The key_func argument allows
	you to customize how the cache key is generated from the function/method
	arguments.

	Args: cache (SingletonCache): The cache instance to use for caching.
	key_func (Callable[[Any, Any], str]): A function that generates the cache
	key from the function/method arguments.

	Returns: Callable: A new function or method that caches the results.

	:param		cache:	   The cache
	:type		cache:	   SingletonCache
	:param		key_func:  The key function
	:type		key_func:  (Callable[[Any, Any], str])
	:param		kwargs:	   The keywords arguments
	:type		kwargs:	   dictionary

	:returns:	decorator
	:rtype:		Callable
	"""

	def decorator(func: Callable) -> Callable:
		@wraps(func)
		def wrapper(*args: Any, **kwargs: Any) -> Any:
			key = key_func(*args, **kwargs)
			cached_value = cache.get(key)
			if cached_value is not None:
				return cached_value
			else:
				result = func(*args, **kwargs)
				cache.set(key, result, time.time())
				return result

		return wrapper

	return decorator
