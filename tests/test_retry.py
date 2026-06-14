import pytest
from utils import retry


def test_retry_succeeds_on_first_try():
    result = retry(lambda: 42, max_retries=3, base_delay=0)
    assert result == 42


def test_retry_succeeds_after_failures():
    call_count = 0

    def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("fail")
        return "ok"

    result = retry(flaky, max_retries=3, base_delay=0, exceptions=(ConnectionError,))
    assert result == "ok"
    assert call_count == 3


def test_retry_raises_after_max_retries():
    def always_fail():
        raise ValueError("always")

    with pytest.raises(ValueError, match="always"):
        retry(always_fail, max_retries=2, base_delay=0, exceptions=(ValueError,))


def test_retry_does_not_catch_unexpected_exceptions():
    def unexpected():
        raise TypeError("unexpected")

    with pytest.raises(TypeError):
        retry(unexpected, max_retries=3, base_delay=0, exceptions=(ValueError,))
