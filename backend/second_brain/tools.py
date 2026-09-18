"""Small, deliberately constrained tools exposed to Jarvis."""
from __future__ import annotations

import platform
import subprocess
import webbrowser
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol, Type
from urllib.parse import quote_plus, urlparse

from pydantic import BaseModel, Field, ValidationError, field_validator

from .models import ToolResult


class SearchArgs(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    service: str = Field(default="youtube")

    @field_validator("service")
    @classmethod
    def service_allowed(cls, value: str) -> str:
        if value.lower() not in {"youtube", "music", "films"}:
            raise ValueError("service must be youtube, music, or films")
        return value.lower()


class AppArgs(BaseModel):
    app: str = Field(min_length=1, max_length=40)


class SmsArgs(BaseModel):
    to: str = Field(pattern=r"^\+[1-9]\d{7,14}$")
    body: str = Field(min_length=1, max_length=1600)


class SmsProvider(Protocol):
    def send(self, to: str, body: str) -> dict[str, Any]: ...


class MockSmsProvider:
    def send(self, to: str, body: str) -> dict[str, Any]:
        return {"provider": "mock", "dry_run": True, "to": to, "body": body}


class TwilioSmsProvider:
    def __init__(self, account_sid: str, auth_token: str, from_number: str) -> None:
        try:
            from twilio.rest import Client
        except ImportError as exc:
            raise RuntimeError("Twilio provider requires the optional 'twilio' package") from exc
        self.client, self.from_number = Client(account_sid, auth_token), from_number

    def send(self, to: str, body: str) -> dict[str, Any]:
        message = self.client.messages.create(body=body, from_=self.from_number, to=to)
        return {"provider": "twilio", "sid": message.sid, "to": to}


@dataclass
class ToolSpec:
    fn: Callable[..., Any]
    requires_confirmation: bool
    description: str
    arguments: Type[BaseModel] | None = None
    confirmation_details: str | None = None
    timeout: float = 10.0


class ToolRegistry:
    def __init__(self, sandbox: Path) -> None:
        self.sandbox = sandbox.resolve()
        self._tools: dict[str, ToolSpec] = {}

    def register(self, name: str, fn: Callable[..., Any], *, requires_confirmation: bool = True,
                 description: str = "", arguments: Type[BaseModel] | None = None,
                 confirmation_details: str | None = None, timeout: float = 10.0) -> None:
        self._tools[name] = ToolSpec(fn, requires_confirmation, description, arguments,
                                     confirmation_details, timeout)

    def schemas(self) -> list[dict[str, Any]]:
        result = []
        for name, spec in self._tools.items():
            fields = {}
            if spec.arguments:
                for field_name, field in spec.arguments.model_fields.items():
                    fields[field_name] = {
                        "type": "string", "required": field.is_required(),
                        "default": field.default if not field.is_required() else None,
                    }
            result.append({"name": name, "requires_confirmation": spec.requires_confirmation,
                           "description": spec.description, "arguments": fields,
                           "confirmation_details": spec.confirmation_details})
        return result

    def path(self, requested: str) -> Path:
        candidate = (self.sandbox / requested).resolve()
        if candidate != self.sandbox and self.sandbox not in candidate.parents:
            raise ValueError("path escapes sandbox")
        return candidate

    def execute(self, name: str, arguments: dict[str, Any], confirmed: bool = False) -> ToolResult:
        spec = self._tools.get(name)
        if spec is None:
            return ToolResult(ok=False, error="unknown tool")
        if spec.requires_confirmation and not confirmed:
            return ToolResult(ok=False, requires_confirmation=True,
                              error="confirmation required",
                              output={"tool": name, "details": spec.confirmation_details,
                                      "arguments": arguments})
        try:
            values = spec.arguments(**arguments) if spec.arguments else arguments
            pool = ThreadPoolExecutor(max_workers=1)
            future = pool.submit(spec.fn, **(values.model_dump() if isinstance(values, BaseModel) else values))
            try:
                result = future.result(timeout=spec.timeout)
            except TimeoutError:
                future.cancel()
                pool.shutdown(wait=False, cancel_futures=True)
                return ToolResult(ok=False, error=f"tool timed out after {spec.timeout:g}s")
            except Exception:
                pool.shutdown(wait=True)
                raise
            pool.shutdown(wait=True)
            return ToolResult(ok=True, output=result)
        except TimeoutError:
            return ToolResult(ok=False, error=f"tool timed out after {spec.timeout:g}s")
        except (TypeError, ValueError, OSError, ValidationError, RuntimeError) as exc:
            return ToolResult(ok=False, error=str(exc))


SEARCH_URLS = {
    "youtube": "https://www.youtube.com/results?search_query={}",
    "music": "https://open.spotify.com/search/{}",
    "films": "https://www.imdb.com/find/?q={}",
}
ALLOWED_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
}


def search_url(query: str, service: str = "youtube") -> dict[str, str]:
    args = SearchArgs(query=query, service=service)
    url = SEARCH_URLS[args.service].format(quote_plus(args.query))
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc not in {"www.youtube.com", "open.spotify.com", "www.imdb.com"}:
        raise ValueError("generated URL is not allowlisted")
    if not webbrowser.open(url, new=2):
        raise RuntimeError("browser could not open the URL")
    return {"service": args.service, "query": args.query, "url": url}


def launch_app(app: str) -> dict[str, str]:
    key = app.lower().strip()
    executable = ALLOWED_APPS.get(key)
    if not executable:
        raise ValueError(f"app is not allowlisted: {app}")
    if platform.system() != "Windows":
        raise RuntimeError("desktop app launch is only supported on Windows")
    subprocess.Popen([executable], shell=False, close_fds=True)
    return {"app": key, "executable": executable, "status": "started"}


def send_sms(provider: SmsProvider, to: str, body: str) -> dict[str, Any]:
    args = SmsArgs(to=to, body=body)
    return provider.send(args.to, args.body)


def register_builtin_tools(registry: ToolRegistry, provider: SmsProvider | None = None) -> None:
    sms = provider or MockSmsProvider()
    registry.register("search_web", search_url, requires_confirmation=False,
                     description="Search YouTube, music, or films in an allowlisted browser site.",
                     arguments=SearchArgs, timeout=8)
    registry.register("open_app", launch_app, description="Open one allowlisted Windows desktop app.",
                     arguments=AppArgs, confirmation_details="This starts an application on this computer.",
                     timeout=5)
    registry.register("send_sms", lambda to, body: send_sms(sms, to, body),
                     description="Send a text message through the configured provider.",
                     arguments=SmsArgs,
                     confirmation_details="This sends the exact recipient and message shown above.",
                     timeout=10)
