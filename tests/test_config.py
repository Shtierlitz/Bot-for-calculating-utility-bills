import pytest

from bot.config import Settings, get_settings


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Изолирует тесты от реального окружения и значений из .env."""
    monkeypatch.delenv('BOT_TOKEN', raising=False)
    monkeypatch.delenv('BOT_PARSE_MODE', raising=False)


def test_reads_token_without_parse_mode(monkeypatch):
    monkeypatch.setenv('BOT_TOKEN', 'test-token')

    assert get_settings() == Settings(bot_token='test-token', parse_mode=None)


def test_reads_optional_parse_mode(monkeypatch):
    monkeypatch.setenv('BOT_TOKEN', 'test-token')
    monkeypatch.setenv('BOT_PARSE_MODE', 'HTML')

    assert get_settings().parse_mode == 'HTML'


def test_empty_parse_mode_is_none(monkeypatch):
    monkeypatch.setenv('BOT_TOKEN', 'test-token')
    monkeypatch.setenv('BOT_PARSE_MODE', '')

    assert get_settings().parse_mode is None


@pytest.mark.parametrize('token', [None, ''])
def test_missing_token_raises_clear_error(monkeypatch, token):
    if token is not None:
        monkeypatch.setenv('BOT_TOKEN', token)

    with pytest.raises(RuntimeError, match='BOT_TOKEN'):
        get_settings()
