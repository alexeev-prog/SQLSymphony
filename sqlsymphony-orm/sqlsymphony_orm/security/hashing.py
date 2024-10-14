import hashlib
from abc import ABC, abstractmethod
from enum import Enum, auto
from hmac import compare_digest
from typing import Union
from collections import Counter


def distribute(items, num_containers, hash_function=hash):
	return Counter([hash_function(item) % num_containers for item in items])


def plot(histogram):
	for key in sorted(histogram):
		count = histogram[key]
		padding = (max(histogram.values()) - count) * " "
		print(f"{key:3} {'■' * count}{padding} ({count})")


def hash_function(key):
	return sum(
		index * ord(character)
		for index, character in enumerate(repr(key).lstrip("'"), 1)
	)


class HashAlgorithm(Enum):
	SHA256 = auto()
	SHA512 = auto()
	MD5 = auto()
	BLAKE2B = auto()
	BLAKE2S = auto()


class HashingBase(ABC):
	@abstractmethod
	def hash(
		self, data: Union[bytes, str], hexdigest: bool = False
	) -> Union[bytes, str]:
		raise NotImplementedError()

	@abstractmethod
	def verify(self, data: Union[bytes, str], hashed_data: Union[bytes, str]) -> bool:
		raise NotImplementedError()


class PlainHasher(HashingBase):
	def __init__(self, algorithm: HashAlgorithm = HashAlgorithm.SHA256):
		self.algorithm = algorithm

	def hash(self, data: Union[bytes, str]) -> Union[bytes, str]:
		if isinstance(data, str):
			data = data.encode("utf-8")

		hasher = self.get_hasher()
		return hasher(data).digest()

	def verify(self, data: Union[bytes, str], hashed_data: Union[bytes, str]) -> bool:
		if isinstance(data, str):
			data = data.encode("utf-8")
		if isinstance(hashed_data, str):
			hashed_data = hashed_data.encode()

		expected_hash = self.hash(data, hexdigest=False)

		return compare_digest(expected_hash, hashed_data)

	def get_hasher(self) -> callable:
		hash_functions = {
			HashAlgorithm.SHA256: hashlib.sha256,
			HashAlgorithm.SHA512: hashlib.sha512,
			HashAlgorithm.MD5: hashlib.md5,
			HashAlgorithm.BLAKE2B: hashlib.blake2b,
			HashAlgorithm.BLAKE2S: hashlib.blake2s,
		}

		hash_function = hash_functions.get(self.algorithm, None)

		if hash_function is None:
			raise ValueError(f"Unknown hash function type: {self.algorithm}")
		else:
			return hash_function


class SaltedHasher(HashingBase):
	def __init__(
		self, algorithm: HashAlgorithm = HashAlgorithm.SHA256, salt: str = "SOMESALT"
	):
		self.algorithm = algorithm
		self.salt = salt

	def hash(self, data: Union[bytes, str]) -> Union[bytes, str]:
		salt = self.salt.encode("utf-8")

		if isinstance(data, str):
			data = data.encode("utf-8")

		hasher = self.get_hasher()
		value = f"{data}{salt}".encode("utf-8")

		return hasher(value).digest()

	def verify(self, data: str, hashed_data: Union[bytes, str]) -> bool:
		if isinstance(hashed_data, str):
			print("convert")

		expected_hash = self.hash(data)

		return compare_digest(expected_hash, hashed_data)

	def get_hasher(self) -> callable:
		hash_functions = {
			HashAlgorithm.SHA256: hashlib.sha256,
			HashAlgorithm.SHA512: hashlib.sha512,
			HashAlgorithm.MD5: hashlib.md5,
			HashAlgorithm.BLAKE2B: hashlib.blake2b,
			HashAlgorithm.BLAKE2S: hashlib.blake2s,
		}

		hash_function = hash_functions.get(self.algorithm, None)

		if hash_function is None:
			raise ValueError(f"Unknown hash function type: {self.algorithm}")
		else:
			return hash_function
