from urllib.parse import parse_qs
import hmac, hashlib

def verify_telegram_init_data(init_data: str, bot_token: str) -> bool:
    """
    Проверить подлинность initData от Telegram Mini App.
    """
    params = parse_qs(init_data, keep_blank_values=True)
    data = {k: v[0] for k, v in params.items()}
    hash_received = data.pop('hash', None)
    if not hash_received:
        return False

    check_list = []
    for key, value in data.items():
        check_list.append(f"{key}={value}")
    check_list.sort()
    data_check_string = "\n".join(check_list)

    secret_key = hmac.new(
        key=b"WebAppData", 
        msg=bot_token.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    hmac_obj = hmac.new(
        key=secret_key,
        msg=data_check_string.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    hash_calculated = hmac_obj.hexdigest()

    return hmac.compare_digest(hash_calculated, hash_received)
