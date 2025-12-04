from __future__ import annotations

import sys
from pathlib import Path

from newyearscards import sheets


class FakeResponse:
    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self) -> None:  # pragma: no cover - trivial
        return None


class FakeSession:
    def __init__(self, content: bytes):
        self._content = content

    def get(self, url: str, timeout: int = 30) -> FakeResponse:  # type: ignore[override]
        assert "export?format=csv" in url
        return FakeResponse(self._content)


class FakeCreds:
    @classmethod
    def from_service_account_file(cls, path: str, scopes: list[str]):  # type: ignore[no-untyped-def]
        assert Path(path).exists()
        assert scopes
        return object()


def test_download_sheet_writes_default_and_custom_paths(tmp_path, monkeypatch):
    # Prepare environment
    year = 2099
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    templates = tmp_path / "templates.yml"
    key = tmp_path / "key.json"
    key.write_text("{}", encoding="utf-8")

    monkeypatch.setenv("RAW_DATA_DIR", str(raw_dir))
    monkeypatch.setenv("PROCESSED_DATA_DIR", str(processed_dir))
    monkeypatch.setenv("ADDRESS_TEMPLATES", str(templates))
    monkeypatch.setenv("SERVICE_ACCOUNT_KEY", str(key))
    monkeypatch.setenv("SHEET_URL", "https://docs.google.com/spreadsheets/d/abc123/edit#gid=0")

    # Stub google libraries by injecting into sys.modules
    class ModAuthReq:
        class AuthorizedSession:  # type: ignore[no-redef]
            def __init__(self, _creds):
                pass

            def get(self, url: str, timeout: int = 30) -> FakeResponse:
                return FakeResponse(b"a,b\n1,2\n")

    class ModOAuth2:
        class service_account:  # type: ignore[no-redef]
            Credentials = FakeCreds

    monkeypatch.setitem(sys.modules, "google.auth.transport.requests", ModAuthReq())
    monkeypatch.setitem(sys.modules, "google.oauth2", ModOAuth2())

    # Default path
    out1 = sheets.download_sheet(year)
    assert out1.exists()
    assert out1.parent.name == str(year)
    assert out1.name == "mailing_list.csv"
    assert out1.read_text(encoding="utf-8").startswith("a,b")

    # Custom path (file)
    out_file = tmp_path / "custom.csv"
    out2 = sheets.download_sheet(year, out_path=out_file)
    assert out2 == out_file
    assert out2.exists()

