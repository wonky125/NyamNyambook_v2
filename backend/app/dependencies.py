import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

bearer_scheme = HTTPBearer()

# Supabase JWKS 캐시 (서버 재시작 전까지 유지)
_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    """Supabase JWKS 공개키 목록을 가져온다 (ES256 검증용)."""
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json",
                timeout=10.0,
            )
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Supabase JWT를 검증하고 user_id(UUID 문자열)를 반환한다.

    최신 Supabase는 ES256(ECDSA)을 사용하므로 JWKS에서 공개키를 가져와 검증한다.
    구형 프로젝트 호환을 위해 HS256도 지원한다.
    """
    token = credentials.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg", "HS256")
        kid = unverified_header.get("kid")

        if alg == "ES256":
            # 최신 Supabase: JWKS 공개키로 검증
            jwks = await _get_jwks()
            signing_key = next(
                (k for k in jwks.get("keys", []) if k.get("kid") == kid),
                None,
            )
            if signing_key is None:
                raise JWTError(f"JWKS에서 kid={kid} 키를 찾을 수 없습니다")
            key = signing_key
        else:
            # 구형 Supabase: HS256 공유 시크릿으로 검증
            key = settings.SUPABASE_JWT_SECRET

        payload = jwt.decode(
            token,
            key,
            algorithms=[alg],
            options={"verify_aud": False},
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
            )
        return user_id

    except HTTPException:
        raise
    except JWTError as e:
        print(f"[AUTH] JWT 검증 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증에 실패했습니다. 다시 로그인해주세요.",
        )
