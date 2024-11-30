from sqlsymphony_orm.security.hashing import PlainHasher, HashAlgorithm

hasher = PlainHasher(
    HashAlgorithm.SHA512
)  # also: SHA256, SHA512, MD5, BLAKE2B, BLAKE2S

hash1 = hasher.hash("password")
hash2 = hasher.hash("pasword")

print(hasher.verify("password", hash1))  # True
print(hasher.verify("password", hash2))  # False
