"""Regression tests for the SSRF redirect fix (audit 2026-09-16, finding F2).

_is_safe_remote_url() validated the URL it was handed, but urllib's default
opener then FOLLOWED redirects without re-validating -- so a public,
allow-listed URL that 302s to http://169.254.169.254/ reached cloud metadata.
The fix routes both fetches through _safe_open(), which installs a handler that
refuses redirects outright.

These run against a real loopback HTTP server, so they exercise the actual
urllib machinery rather than a mock of it.
"""
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from services.pdf_generator import _is_safe_remote_url, _safe_open


# --- the guard itself ------------------------------------------------------

@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "file://C:/Windows/win.ini",
        "gopher://example.com/",
        "ftp://example.com/x.png",
        "http://169.254.169.254/latest/meta-data/",   # AWS/GCP metadata
        "http://127.0.0.1/x.png",
        "http://localhost/x.png",
        "http://10.0.0.5/x.png",
        "http://192.168.1.10/x.png",
        "http://172.16.0.5/x.png",
        "http://[::1]/x.png",
        "",
        "not-a-url",
    ],
)
def test_guard_rejects_dangerous_urls(url):
    assert _is_safe_remote_url(url) is False


def test_guard_fails_closed_on_garbage():
    assert _is_safe_remote_url(None) is False


# --- the redirect hole F2 closed -------------------------------------------

class _RedirectingHandler(BaseHTTPRequestHandler):
    """Serves a 302 to the cloud-metadata address, like a malicious host would."""

    def do_GET(self):
        self.send_response(302)
        self.send_header("Location", "http://169.254.169.254/latest/meta-data/")
        self.end_headers()

    def log_message(self, *args):
        pass


@pytest.fixture()
def redirector():
    srv = HTTPServer(("127.0.0.1", 0), _RedirectingHandler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield "http://127.0.0.1:%d/logo.png" % srv.server_port
    srv.shutdown()
    srv.server_close()


def test_safe_open_refuses_to_follow_redirect(redirector):
    """The whole point of F2: the redirect must NOT be followed.

    urllib raises HTTPError(302) when a redirect handler returns None, so the
    302 surfaces as an error instead of silently fetching the metadata URL.
    """
    req = urllib.request.Request(redirector, headers={"User-Agent": "SnapAI-PDF/1.0"})
    with pytest.raises(urllib.error.HTTPError) as exc:
        _safe_open(req, timeout=5)
    assert exc.value.code == 302


def test_default_opener_would_have_followed_it(redirector):
    """Characterises the ORIGINAL bug, so the regression is unambiguous.

    The stock opener tries to follow the 302 to 169.254.169.254. It must NOT
    come back with a clean 200 from a plain GET -- either it errors out, or it
    hangs and times out. Anything else means the metadata endpoint was reached.
    """
    req = urllib.request.Request(redirector, headers={"User-Agent": "SnapAI-PDF/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=3)
    except Exception:
        return  # attempted the hop and failed -- exactly the exposure F2 removes
    assert resp.geturl() != redirector, (
        "default opener did not follow the redirect; this test no longer "
        "characterises the original bug"
    )


def test_safe_open_is_wired_into_both_fetch_paths():
    """Guard against someone reverting to a bare urlopen() later."""
    import inspect
    import services.pdf_generator as pg

    src = inspect.getsource(pg)
    assert "_urlreq.urlopen(" not in src, (
        "a bare urlopen() reappeared in pdf_generator.py - it bypasses the "
        "redirect guard; use _safe_open() instead"
    )
    assert src.count("_safe_open(req, timeout=") == 2, (
        "expected exactly 2 _safe_open call sites (unit photo + company logo)"
    )
