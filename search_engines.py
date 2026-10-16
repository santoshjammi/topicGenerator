"""Search-engine suggestion clients with consistent error handling."""
from collections.abc import Callable
from typing import ClassVar, Union

import requests

import config
from file_writter import FileWriter

SuggestionResult = Union[tuple[str, ...], tuple[bool, str]]  # noqa: UP007


class SearchEngineSuggestions:
    headers: ClassVar[dict[str, str]] = {"user-agent": config.user_agent}

    @staticmethod
    def _get_json(url: str, params: dict) -> object:
        response = requests.get(
            url, params=params, headers=SearchEngineSuggestions.headers,
            timeout=config.timeout,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _result(callable_: Callable[[], object]) -> SuggestionResult:
        try:
            payload = callable_()
            return tuple(payload)
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
            return False, str(exc)

    @staticmethod
    def get_yahoo(kw: str) -> SuggestionResult:
        return SearchEngineSuggestions._result(
            lambda: [item["key"] for item in SearchEngineSuggestions._get_json(
                "https://search.yahoo.com/sugg/gossip/gossip-us-ura/",
                {"command": kw.casefold(), "output": "json", "nresults": 20},
            )["gossip"]["results"]]
        )

    @staticmethod
    def get_ask(kw: str) -> SuggestionResult:
        return SearchEngineSuggestions._result(
            lambda: SearchEngineSuggestions._get_json(
                "https://amg-ss.ask.com/query", {"limit": 20, "q": kw.casefold()}
            )[1]
        )

    @staticmethod
    def get_yandex_us(kw: str) -> SuggestionResult:
        return SearchEngineSuggestions._result(
            lambda: SearchEngineSuggestions._get_json(
                "https://yandex.com/suggest/suggest-ya.cgi",
                {"v": 4, "bemjson": 0, "part": kw.casefold()},
            )[1]
        )

    @staticmethod
    def get_duckduckgo(kw: str) -> SuggestionResult:
        return SearchEngineSuggestions._result(
            lambda: [item["phrase"] for item in SearchEngineSuggestions._get_json(
                "https://duckduckgo.com/ac/", {"q": kw.casefold()}
            )]
        )

    @staticmethod
    def get_ecosia(kw: str) -> SuggestionResult:
        return SearchEngineSuggestions._result(
            lambda: SearchEngineSuggestions._get_json(
                "https://ac.ecosia.org/", {"q": kw.casefold()}
            )["suggestions"]
        )

    @staticmethod
    def get_brave(kw: str) -> SuggestionResult:
        return SearchEngineSuggestions._result(
            lambda: SearchEngineSuggestions._get_json(
                "https://search.brave.com/api/suggest", {"q": kw.casefold()}
            )[1]
        )

    @staticmethod
    def get_google(kw: str) -> SuggestionResult:
        return SearchEngineSuggestions._result(
            lambda: SearchEngineSuggestions._get_json(
                "https://www.google.com/complete/search",
                {"q": kw.casefold(), "client": "firefox"},
            )[1]
        )

    @staticmethod
    def get_bing(kw: str) -> SuggestionResult:
        return SearchEngineSuggestions._result(
            lambda: SearchEngineSuggestions._get_json(
                "https://api.bing.com/osjson.aspx", {"query": kw.casefold()}
            )[1]
        )

    @staticmethod
    def kw_results(search_engine: Callable[[str], SuggestionResult], kw: str) -> tuple[str, ...]:
        result = search_engine(kw)
        if result and result[0] is False:
            FileWriter.write_log(str(result[1]))
            return ()
        return tuple(result)
