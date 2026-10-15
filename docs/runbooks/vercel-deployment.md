# Vercel 배포 준비

현재는 설정 안내이며 실제 프로젝트 등록·DB 연결·배포는 수행하지 않았습니다.

## 1. 배포 단위

동일 Git 저장소를 Vercel 프로젝트 두 개로 연결하는 기본안입니다.

| 항목 | 웹 | API |
| --- | --- | --- |
| Root Directory | `apps/web` | `apps/backend` |
| 프레임워크 | Next.js | FastAPI |
| 진입점 | App Router | `app.py`의 ASGI `app` |
| 빌드 | web 패키지의 `npm run build` | Python 의존성 설치 및 ASGI 감지 |
| 영구 데이터 | 브라우저 설정만 localStorage | 현재 fixture, 이후 외부 PostgreSQL |

모노레포 루트의 npm workspaces와 lockfile을 유지합니다. 실제 Vercel import 시 루트 밖 workspace 접근 및 설치 명령을 확인합니다.

API는 `requirements.txt`의 고정 런타임 의존성을 사용합니다. 로컬 테스트 환경은 `requirements-dev.txt`로 별도 관리합니다. Vercel이 pyproject와 requirements 중 어떤 설치 경로를 선택했는지 빌드 로그에서 확인하고, 운영 도입 전 같은 의존성으로 고정합니다.

## 2. 배포 순서

1. API 프로젝트를 배포하고 `/health/ready`, `/api/v1/dashboard`, `/docs` 확인.
2. 웹 프로젝트의 서버 환경변수 `BACKEND_URL`에 API의 HTTPS origin 설정. `/api/v1`은 붙이지 않습니다.
3. 웹을 빌드/배포. 해당 값은 Next.js rewrite의 **빌드 시점**에 반영되므로 변경 후 재배포합니다.
4. 웹의 `/api/v1/dashboard`가 정상 응답하는지 확인.
5. 시장 필터·섹터 상세·관계 기간 변경·모바일 레이아웃 확인.
6. 프리뷰 환경도 대응하는 API 주소를 사용하도록 환경별로 지정.

`BACKEND_URL`이 없으면 로컬 API 주소로 연결됩니다. 배포 시 반드시 올바른 값을 지정합니다. 브라우저는 같은 웹 origin으로 요청하고 Next.js rewrite가 API로 전달하므로 API 주소를 공개 환경변수로 복제하지 않습니다.

## 3. 현재 공개 범위

- 현재 API에는 합성 공개 예시만 있습니다. 인증·유료 공급자·개인 데이터는 연결하지 않았습니다.
- 실데이터/개인 데이터 연결 전에는 API 직접 호출에도 인증·권한·요청량 제한을 적용해야 합니다.
- Vercel Deployment Protection을 사용하면 프로젝트 간 요청도 허용되도록 설정해야 합니다. 인증 보호를 제거하는 방식으로 해결하지 않습니다.
- 웹은 API에만 접근하고 Python이 계산합니다. Next.js에 별도 점수 로직을 만들지 않습니다.
- 로컬 파일 쓰기, 프로세스 메모리, 요청 후 단순 백그라운드 태스크를 영구 작업으로 사용하지 않습니다.

## 4. 실데이터 단계에서 추가할 것

- 외부 PostgreSQL 공급자·리전·연결 풀링·백업.
- 실제 요금제의 함수 시간·메모리·번들 제한 확인.
- 공급자별 비밀키, 허용된 저장·배포 범위.
- 수집/작업 이력·재시도·중복 방지·완료 스냅샷 공개.
- 오래 걸리는 백필·관계 계산을 실행할 환경.
- 인증된 Cron 진입점. 아직 Cron을 활성화하지 않습니다.

이 첫 버전은 Vercel에서의 원격 빌드/런타임 검증 전 상태입니다. 로컬 빌드 성공만으로 원격 배포 성공을 주장하지 않습니다.
