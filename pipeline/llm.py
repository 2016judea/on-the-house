"""The one door to a model. Every agent step goes through here.

Runs the Claude Code CLI headless (`claude -p`), which bills to Aidan's existing
subscription: $0 marginal per call, no API key spent. Swap for the Anthropic API
here, and only here, if a batch outgrows it.
"""
from __future__ import annotations

import json
import re
import subprocess


def ask(prompt: str, *, web: bool = False, model: str = "sonnet", timeout: int = 600) -> str:
    cmd = ["claude", "-p", "--model", model]
    if web:
        cmd += ["--allowedTools", "WebSearch,WebFetch"]
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd="/tmp")
    if r.returncode != 0:
        raise RuntimeError(f"claude -p failed: {r.stderr[-500:]}")
    return r.stdout.strip()


def ask_json(prompt: str, **kw):
    out = ask(prompt + "\n\nReturn ONLY valid JSON. No prose, no code fence.", **kw)
    m = re.search(r"(\{.*\}|\[.*\])", out, re.S)
    if not m:
        raise ValueError(f"no JSON in reply: {out[:300]}")
    return json.loads(m.group(1))
