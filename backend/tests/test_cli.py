import pytest
from conftest import FakeClient, make_settings, text_response

from harness_demo.__main__ import build_parser, main


def test_list_does_not_load_configuration(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fail_if_called() -> None:
        raise AssertionError("list must not load settings")

    monkeypatch.setattr("harness_demo.__main__.load_settings", fail_if_called)
    assert main(["list"]) == 0
    assert "Demo" in capsys.readouterr().out


def test_invalid_demo_does_not_load_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called() -> None:
        raise AssertionError("invalid demo must not load settings")

    monkeypatch.setattr("harness_demo.__main__.load_settings", fail_if_called)
    assert main(["7"]) == 2


def test_cli_help_has_no_alternate_model_mode() -> None:
    help_text = build_parser().format_help().lower()
    for forbidden in ("fake", "scripted", "mock"):
        assert forbidden not in help_text


def test_cli_dispatches_demo_with_injected_client() -> None:
    client = FakeClient([text_response("只收到工单，无法确定具体规则。")])
    assert main(["1"], settings=make_settings(), client=client) == 0
    assert len(client.responses.calls) == 1
