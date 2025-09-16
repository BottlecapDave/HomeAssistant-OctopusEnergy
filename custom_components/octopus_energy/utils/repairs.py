import hashlib

def hash_ids(*ids: str) -> list[str]:
  return [hashlib.sha256(i.encode("utf-8")).hexdigest() for i in ids]

def safe_repair_key(key: str, *ids: str) -> str:
  return key.format(*hash_ids(*ids))