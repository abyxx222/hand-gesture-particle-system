from pathlib import Path
from typing import Any, Callable
from .models import ToolResult


class ToolRegistry:
    def __init__(self, sandbox: Path) -> None:
        self.sandbox = sandbox.resolve()
        self._tools: dict[str, tuple[Callable[..., Any], bool, str]] = {}

    def register(self, name: str, fn: Callable[..., Any], *, requires_confirmation: bool = True,
                 description: str = "") -> None:
        self._tools[name] = (fn, requires_confirmation, description)

    def schemas(self) -> list[dict[str, Any]]:
        return [{"name": name, "requires_confirmation": confirm, "description": description}
                for name, (_, confirm, description) in self._tools.items()]

    def path(self, requested: str) -> Path:
        candidate = (self.sandbox / requested).resolve()
        if candidate != self.sandbox and self.sandbox not in candidate.parents:
            raise ValueError("path escapes sandbox")
        return candidate

    def execute(self, name: str, arguments: dict[str, Any], confirmed: bool = False) -> ToolResult:
        if name not in self._tools:
            return ToolResult(ok=False, error="unknown tool")
        fn, needs_confirmation, _ = self._tools[name]
        if needs_confirmation and not confirmed:
            return ToolResult(ok=False, requires_confirmation=True, error="confirmation required")
        try:
            return ToolResult(ok=True, output=fn(**arguments))
        except (TypeError, ValueError, OSError) as exc:
            return ToolResult(ok=False, error=str(exc))
