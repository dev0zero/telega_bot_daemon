import hashlib
import json

def sha256_any(value):
    # Если уже bytes — хешируем напрямую
    if isinstance(value, bytes):
        data = value
    else:
        # Стабильная сериализация любых данных
        data = json.dumps(value, sort_keys=True).encode()

    return hashlib.sha256(data).hexdigest()