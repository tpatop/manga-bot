import hashlib


async def hash_full_text(text: str) -> str:
    if text is not None:
        f = hashlib.sha224()
        f.update(text.encode())
        return f.hexdigest()
    return None
