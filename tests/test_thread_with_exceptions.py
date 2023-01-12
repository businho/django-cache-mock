import pytest

from tests.thread_with_exceptions import Thread


def test_thread_error():
    """Just a sane check that _Thread really raises exceptions."""
    thread = Thread(target=lambda: 1 / 0)
    thread.start()

    with pytest.raises(ZeroDivisionError):
        thread.join()
