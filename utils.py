import time
import logging

logger = logging.getLogger(__name__)


def retry(fn, max_retries=3, base_delay=2, exceptions=(Exception,)):
    for attempt in range(max_retries):
        try:
            return fn()
        except exceptions as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning("Retry %d/%d after %.1fs: %s", attempt + 1, max_retries, delay, e)
            time.sleep(delay)
