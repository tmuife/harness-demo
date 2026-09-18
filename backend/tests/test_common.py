import pytest
from conftest import CORRECT_IMPLEMENTATION

from harness_demo.common import (
    changed_files,
    prepare_workspace,
    run_tests,
    truncate,
    workspace_passed,
    workspace_path,
    write_implementation,
)


def test_prepare_workspace_resets_and_isolates_modes() -> None:
    plain = prepare_workspace(1, False)
    original = (plain / "src/shipping.py").read_text(encoding="utf-8")
    (plain / "src/shipping.py").write_text("changed", encoding="utf-8")

    reset_plain = prepare_workspace(1, False)
    harness = prepare_workspace(1, True)

    assert (reset_plain / "src/shipping.py").read_text(encoding="utf-8") == original
    assert harness != reset_plain
    assert (harness / "src/shipping.py").read_text(encoding="utf-8") == original


def test_workspace_path_rejects_escape() -> None:
    workspace = prepare_workspace(2, True)
    with pytest.raises(ValueError, match="超出"):
        workspace_path(workspace, "../outside.txt")
    with pytest.raises(ValueError, match="相对路径"):
        workspace_path(workspace, "/tmp/outside.txt")


def test_write_implementation_rejects_other_files() -> None:
    workspace = prepare_workspace(2, True)
    with pytest.raises(ValueError, match="只允许"):
        write_implementation(workspace, "changed", "tests/test_shipping.py")


def test_fixture_fails_then_correct_implementation_passes() -> None:
    workspace = prepare_workspace(3, True)
    initial = run_tests(workspace, 10)
    assert not initial.passed
    assert "3 failed" in initial.output

    write_implementation(workspace, CORRECT_IMPLEMENTATION, "src/shipping.py")
    corrected = run_tests(workspace, 10)

    assert corrected.passed
    assert changed_files(workspace) == ["src/shipping.py"]
    assert workspace_passed(workspace, corrected)


def test_truncate_marks_omitted_content() -> None:
    assert truncate("abcdef", 3) == "abc\n... [已截断 3 个字符]"
