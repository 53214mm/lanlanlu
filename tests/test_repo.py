import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def repo_text_files():
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split("\n")
    return [p for p in out if p.endswith((".md", ".json", ".py", ".txt"))]


def test_mcp_config_example_uses_env_placeholder():
    cfg = json.loads(read("mcp-config.example.json"))
    server = cfg["mcpServers"]["mcd-mcp"]
    assert server["type"] == "streamablehttp"
    assert server["url"] == "https://mcp.mcd.cn"
    assert server["headers"]["Authorization"] == "Bearer ${MCD_MCP_TOKEN}"


def test_no_real_token_in_repo():
    leak = re.compile(r"Bearer\s+(?!\$\{MCD_MCP_TOKEN\}|YOUR_MCP_TOKEN)[A-Za-z0-9._\-]{16,}")
    for path in repo_text_files():
        assert not leak.search(read(path)), f"possible token in {path}"


def test_contest_declaration_is_official_text():
    text = read("CONTEST_DECLARATION.md")
    assert text.startswith("# 参赛声明")
    assert "## 信息安全声明" in text
