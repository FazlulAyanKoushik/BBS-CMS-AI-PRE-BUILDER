from __future__ import annotations

import pytest

from app.agents import AIAgent1
from app.config import reload_settings
from app.csv_loader import build_profile, build_profiles_from_file, read_csv_bytes
from app.llm import GeminiProvider, MockProvider, get_provider, provider_name
from app.schemas import SiteSpec

SAMPLE = "sample_inputs/infobix2_20260817191747.csv"


def test_read_csv_header_only_sample_is_tolerated():
    profiles = build_profiles_from_file(SAMPLE)
    assert len(profiles) == 1
    assert profiles[0]["store_name"] is None


def test_read_csv_utf8_with_data_row():
    data = (
        'シリアル,店舗名,業態,キーワード_都道府県,キーワード_市区町村\r\n'
        '1,株式会社サンプル,IT企業,東京都,渋谷区\r\n'
    ).encode("utf-8")
    df = read_csv_bytes(data)
    assert list(df.columns) == ["シリアル", "店舗名", "業態", "キーワード_都道府県", "キーワード_市区町村"]
    profile = build_profile(data)
    assert profile["store_name"] == "株式会社サンプル"
    assert profile["business_type"] == "IT企業"
    assert profile["region"]["prefecture"] == "東京都"
    assert profile["region"]["city"] == "渋谷区"


def test_read_csv_shift_jis_with_data_row():
    data = "店舗名,業態\r\n株式会社テスト,飲食店\r\n".encode("cp932")
    profile = build_profile(data)
    assert profile["store_name"] == "株式会社テスト"
    assert profile["business_type"] == "飲食店"


def test_agent_mock_produces_valid_spec():
    profile = build_profiles_from_file(SAMPLE)[0]
    agent = AIAgent1(provider=MockProvider())
    spec = agent.generate(profile, {"language": "ja"})
    assert isinstance(spec, SiteSpec)
    assert [p.page_name for p in spec.pages] == ["top", "service", "company", "contact"]
    assert spec.language == "ja"
    assert spec.suggested_site_type == "company_website"


def test_agent_falls_back_to_mock_on_invalid_llm_output(tmp_path):
    class BadProvider(MockProvider):
        def generate_structured_spec(self, business_profile, criteria):
            return {"this": "is", "not": "a spec"}

    profile = build_profiles_from_file(SAMPLE)[0]
    agent = AIAgent1(provider=BadProvider())
    spec = agent.generate(profile, criteria={})
    assert isinstance(spec, SiteSpec)
    assert len(spec.pages) == 4


def test_build_profile_empty_bytes_raises():
    with pytest.raises(ValueError):
        build_profile(b"", row_index=0)


def test_provider_name_routing(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    reload_settings()
    assert provider_name() == "gemini"
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    reload_settings()
    assert provider_name() == "mock"
    monkeypatch.setenv("LLM_PROVIDER", "bogus")
    reload_settings()
    assert provider_name() == "mock"


def test_get_provider_returns_mock_by_default(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    reload_settings()
    assert isinstance(get_provider(), MockProvider)


def test_gemini_provider_requires_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    reload_settings()
    # With no API key, should fall back to mock
    assert isinstance(get_provider(), MockProvider)


def test_gemini_provider_reads_model_from_env_at_runtime(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.6-flash")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key-for-construction")
    provider = GeminiProvider()
    assert provider.model == "gemini-3.6-flash"