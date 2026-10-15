"""User-run credential setup. Secrets go only to Toss and a gitignored local file.

This script is intentionally separate from web requests: issuing a new token
invalidates a previous one. Never run it automatically in Vercel cold starts.
"""
import getpass
import json
import os
import re
import ssl
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

def main():
    print("토스증권 공식 OAuth2 토큰 발급입니다. 새 발급은 기존 토큰을 무효화할 수 있습니다.")
    print("계좌·주문 API는 호출하지 않습니다. Client ID/Secret은 저장하지 않습니다.")
    if input("발급을 진행하려면 yes를 입력하세요: ").strip()!="yes":
        return
    client_id=getpass.getpass("Client ID (화면에 표시되지 않음): ").strip()
    client_secret=getpass.getpass("Client Secret (화면에 표시되지 않음): ").strip()
    if not client_id or not client_secret:
        raise SystemExit("Client ID와 Secret이 필요합니다.")
    body=urlencode(dict(grant_type="client_credentials",client_id=client_id,client_secret=client_secret)).encode()
    request=Request("https://openapi.tossinvest.com/oauth2/token",data=body,headers={"Content-Type":"application/x-www-form-urlencoded"},method="POST")
    try:
        with urlopen(request,timeout=15,context=ssl.create_default_context(cafile=certifi.where())) as response:
            data=json.load(response)
    except HTTPError as exc:
        raise SystemExit(f"토큰 발급 실패 (HTTP {exc.code}). 자격증명·허용 IP·요청 제한을 공식 문서에서 확인하세요.") from None
    except (URLError,TimeoutError,ValueError):
        raise SystemExit("토큰 발급 서버에 연결하지 못했습니다. 비밀 값은 출력하지 않습니다.") from None
    token=data.get("access_token")
    expiry=data.get("expires_in")
    if not isinstance(token,str) or not token or "\n" in token or not isinstance(expiry,int) or expiry<=0:
        raise SystemExit("토큰 응답 형식이 올바르지 않습니다.")
    root=Path(__file__).resolve().parents[1]
    target=root/".env.local"
    content=target.read_text() if target.exists() else ""
    content=re.sub(r"(?m)^TOSS_ACCESS_TOKEN(?:_EXPIRES_AT)?=.*\n?", "", content)
    expires_at=(datetime.now(timezone.utc)+timedelta(seconds=expiry)).isoformat()
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,"w") as f:
        f.write(content.rstrip()+f"\nTOSS_ACCESS_TOKEN={token}\nTOSS_ACCESS_TOKEN_EXPIRES_AT={expires_at}\n")
    os.chmod(target,0o600)
    print("발급 완료: Git에서 제외된 .env.local에만 저장했습니다. 토큰 값은 출력하지 않습니다.")
    print("로컬에서는 npm run dev를 재시작하세요. Vercel은 백엔드 환경변수 TOSS_ACCESS_TOKEN에 직접 설정해야 합니다.")
    print(f"만료 시각(UTC): {expires_at}")

if __name__=="__main__":
    main()
