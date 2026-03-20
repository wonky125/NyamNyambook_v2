"""Rate limiter 싱글톤 — 앱 전체에서 공유"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
