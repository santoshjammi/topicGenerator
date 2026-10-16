"""Regression tests for deterministic, offline repository behavior."""

import pandas as pd
import pytest

import config
from file_writter import FileWriter
from filter_keywords import filter_output_keywords
from getInputs import BASE_DIR, append_unique_lines, collect_text_files
from google_trends_checker import check_google_trends
from main import collect_suggestions
from search_engines import SearchEngineSuggestions


def test_search_engine_uses_query_params_and_handles_http_errors(monkeypatch):
    calls = {}

    class Response:
        def raise_for_status(self):
            raise __import__("requests").HTTPError("blocked")

        def json(self):
            return [None, ["ignored"]]

    def fake_get(url, **kwargs):
        calls.update(url=url, kwargs=kwargs)
        return Response()

    monkeypatch.setattr("search_engines.requests.get", fake_get)
    result = SearchEngineSuggestions.get_google("red & blue")
    assert result[0] is False
    assert calls["kwargs"]["params"]["q"] == "red & blue"
    assert "&" not in calls["url"]


def test_collect_suggestions_deduplicates_and_is_offline():
    def fake_getter(keyword):
        return (f"{keyword} result", "shared")

    result = collect_suggestions(["seed"], {"fake": fake_getter})
    assert "shared" in result
    assert len(result) == 27  # one unique result per alphabet suffix plus shared


def test_file_writer_merges_without_duplicates(tmp_path, monkeypatch):
    output = tmp_path / "output.txt"
    log = tmp_path / "log.txt"
    monkeypatch.setattr(config, "output_file", str(output))
    monkeypatch.setattr(config, "log_file", str(log))
    FileWriter.write_txt(("beta", "alpha", "beta"))
    FileWriter.write_txt(("alpha", "gamma"))
    assert output.read_text().splitlines() == ["alpha", "beta", "gamma"]


def test_input_import_is_idempotent(tmp_path):
    source = tmp_path / "source.txt"
    target = tmp_path / "input.txt"
    source.write_text("one\none\ntwo\n")
    assert append_unique_lines([source], target) == 2
    assert append_unique_lines([source], target) == 0
    assert target.read_text().splitlines() == ["one", "two"]


def test_keyword_sources_keep_tooling_keywords_as_data():
    source_names = {path.name for path in collect_text_files(BASE_DIR / "texts")}
    assert "tooling_keywords.txt" in source_names
    assert "requirements.txt" not in source_names


def test_filter_is_case_insensitive_and_unique(tmp_path):
    source = tmp_path / "output.txt"
    destination = tmp_path / "filtered.txt"
    source.write_text("Linux command\nwindows\nLINUX command\nother\n")
    assert filter_output_keywords(["linux"], source, destination)
    assert destination.read_text().splitlines() == ["LINUX command", "Linux command"]


def test_empty_trends_run_writes_schema(tmp_path, monkeypatch):
    class FakeTrendReq:
        def __init__(self, **kwargs):
            pass

        def build_payload(self, *args, **kwargs):
            pass

        def interest_over_time(self):
            return pd.DataFrame()

    monkeypatch.setattr("pytrends.request.TrendReq", FakeTrendReq, raising=False)
    keywords = tmp_path / "keywords.txt"
    output = tmp_path / "results.csv"
    keywords.write_text("")
    result = check_google_trends(str(keywords), str(output), delay_range=(0, 0))
    assert next(iter(result.columns)) == "keyword"
    assert output.exists()


def test_trends_rejects_invalid_batch_size(tmp_path):
    with pytest.raises(ValueError):
        check_google_trends(str(tmp_path / "missing"), str(tmp_path / "out"), batch_size=0)
