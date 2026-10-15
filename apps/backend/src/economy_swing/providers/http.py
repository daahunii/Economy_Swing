"""Bounded HTTPS transport. Never expose provider URLs/headers in errors."""
import json
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

MAX_BYTES = 8 * 1024 * 1024

class ProviderError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code

def get_bytes(url: str, *, headers: dict | None = None, timeout: float = 7) -> bytes:
    request = Request(url, headers={"User-Agent": "EconomySwing/0.2 (research data reader)", **(headers or {})})
    try:
        with urlopen(request, timeout=timeout, context=ssl.create_default_context(cafile=certifi.where())) as response:
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise ProviderError("oversized", "공급자 응답이 허용 크기를 초과했습니다.")
            return body
    except HTTPError as exc:
        messages = {401: "인증 토큰이 없거나 만료되었습니다.", 403: "호출 IP 또는 데이터 이용 권한을 확인해 주세요.", 429: "공급자의 요청 제한에 도달했습니다."}
        raise ProviderError(f"http-{exc.code}", messages.get(exc.code, "공급자 데이터 요청에 실패했습니다.")) from None
    except (URLError, TimeoutError, OSError):
        raise ProviderError("network", "공급자 연결에 실패했습니다. 잠시 후 다시 확인해 주세요.") from None

def get_json(url: str, *, headers: dict | None = None) -> dict:
    try:
        payload = json.loads(get_bytes(url, headers=headers))
        if not isinstance(payload, dict):
            raise ProviderError("invalid-response", "공급자의 응답 형식이 올바르지 않습니다.")
        return payload
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ProviderError("invalid-response", "공급자가 올바른 JSON 자료를 반환하지 않았습니다.") from None
