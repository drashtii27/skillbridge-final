from loguru import logger
from ..core.config import get_settings

_posthog = None


def _get_posthog():
    global _posthog
    if _posthog is None:
        settings = get_settings()
        if settings.posthog_api_key:
            try:
                import posthog
                posthog.project_api_key = settings.posthog_api_key
                posthog.host = settings.posthog_host
                _posthog = posthog
            except ImportError:
                logger.warning("posthog package not installed")
    return _posthog


def track(user_id: str, event: str, properties: dict = None):
    ph = _get_posthog()
    if ph:
        try:
            ph.capture(str(user_id), event, properties or {})
        except Exception as e:
            logger.warning(f"PostHog track failed: {e}")
