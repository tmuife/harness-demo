"""Small deterministic helpers shared by the three demonstrations."""

from __future__ import annotations

import difflib
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = PROJECT_ROOT / "fixtures" / "shipping"
WORKSPACE_ROOT = PROJECT_ROOT / ".demo-workspace"
VALID_DEMOS = {1, 2, 3, 4, 5, 6}
IMPLEMENTATION_PATH = Path("src/shipping.py")
MAX_OUTPUT_CHARS = 12_000


@dataclass(frozen=True)
class TestResult:
    returncode: int
    output: str
    timed_out: bool = False

    @property
    def passed(self) -> bool:
        return self.returncode == 0 and not self.timed_out


def truncate(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    omitted = len(text) - limit
    return f"{text[:limit]}\n... [已截断 {omitted} 个字符]"


def prepare_workspace(demo_number: int, harness: bool) -> Path:
    if demo_number not in VALID_DEMOS:
        raise ValueError(f"无效 Demo 编号: {demo_number}")

    mode = "harness" if harness else "plain"
    workspace_root = WORKSPACE_ROOT.resolve()
    destination = (WORKSPACE_ROOT / f"demo-{demo_number}-{mode}").resolve()
    if destination.parent != workspace_root:
        raise ValueError("工作区路径不安全")

    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(FIXTURE_ROOT, destination)
    return destination


def workspace_path(workspace: Path, relative_path: str) -> Path:
    if not relative_path or Path(relative_path).is_absolute():
        raise ValueError("路径必须是工作区内的相对路径")
    root = workspace.resolve()
    candidate = (root / relative_path).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("路径超出当前 Demo 工作区")
    return candidate


def read_workspace_file(workspace: Path, relative_path: str) -> str:
    path = workspace_path(workspace, relative_path)
    if not path.is_file():
        raise ValueError(f"文件不存在: {relative_path}")
    return path.read_text(encoding="utf-8")


def write_implementation(workspace: Path, content: str, relative_path: str) -> None:
    if Path(relative_path).as_posix() != IMPLEMENTATION_PATH.as_posix():
        raise ValueError("只允许写入 src/shipping.py")
    path = workspace_path(workspace, relative_path)
    path.write_text(content, encoding="utf-8")


def write_workspace_file(
    workspace: Path,
    content: str,
    relative_path: str,
    allowed_paths: set[str],
) -> None:
    """Write a text file only when its normalized relative path is explicitly allowed."""
    normalized = Path(relative_path).as_posix()
    if normalized not in allowed_paths:
        raise ValueError(f"不允许写入: {normalized}")
    path = workspace_path(workspace, normalized)
    path.write_text(content, encoding="utf-8")


def run_tests(workspace: Path, timeout_seconds: int) -> TestResult:
    environment = {
        key: os.environ[key]
        for key in ("HOME", "LANG", "LC_ALL", "PATH", "SYSTEMROOT")
        if key in os.environ
    }
    environment["PYTHONPATH"] = str(workspace / "src")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    try:
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=workspace,
            env=environment,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        partial = "".join(part for part in (exc.stdout, exc.stderr) if isinstance(part, str))
        return TestResult(124, truncate(f"{partial}\n测试执行超时", 4_000), timed_out=True)

    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part).strip()
    return TestResult(completed.returncode, truncate(output, 4_000))


def _tracked_files(root: Path) -> dict[str, bytes]:
    ignored_parts = {"__pycache__", ".pytest_cache"}
    files: dict[str, bytes] = {}
    for path in root.rglob("*"):
        if not path.is_file() or any(part in ignored_parts for part in path.parts):
            continue
        if path.suffix == ".pyc":
            continue
        files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def changed_files(workspace: Path) -> list[str]:
    original = _tracked_files(FIXTURE_ROOT)
    current = _tracked_files(workspace)
    names = set(original) | set(current)
    return sorted(name for name in names if original.get(name) != current.get(name))


def implementation_diff(workspace: Path) -> str:
    original = (FIXTURE_ROOT / IMPLEMENTATION_PATH).read_text(encoding="utf-8").splitlines()
    current = (workspace / IMPLEMENTATION_PATH).read_text(encoding="utf-8").splitlines()
    lines = difflib.unified_diff(
        original,
        current,
        fromfile="fixture/src/shipping.py",
        tofile="workspace/src/shipping.py",
        lineterm="",
    )
    return "\n".join(lines) or "(无实现变更)"


def workspace_passed(workspace: Path, test_result: TestResult) -> bool:
    return test_result.passed and changed_files(workspace) == [IMPLEMENTATION_PATH.as_posix()]


def print_header(demo_number: int, title: str, harness: bool, model: str, capability: str) -> None:
    mode = "HARNESS" if harness else "PLAIN"
    print(f"Demo {demo_number}: {title}")
    print(f"模式: {mode}")
    print(f"模型: {model}")
    print(f"实验变量: {capability}")
    print()
