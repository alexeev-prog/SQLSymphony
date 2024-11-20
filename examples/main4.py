from sqlsymphony_orm.security.hashing import SaltedHasher, HashAlgorithm

hasher = SaltedHasher(
	HashAlgorithm.SHA512, salt="SALT"
)  # also: SHA256, SHA512, MD5, BLAKE2B, BLAKE2S
hasher2 = SaltedHasher(
	HashAlgorithm.SHA512, salt="SALT2"
)  # also: SHA256, SHA512, MD5, BLAKE2B, BLAKE2S

hash1 = hasher.hash("password")
hash2 = hasher2.hash("password")

print(hasher.verify("password", hash1))	 # True
print(hasher.verify("password", hash2))	 # False
