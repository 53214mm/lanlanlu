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


TOOLS_USED = [
    "now-time-info", "query-nearby-stores", "delivery-query-addresses",
    "delivery-create-address", "delivery-query-stores", "auto-bind-coupons",
    "query-store-coupons", "query-my-coupons", "query-meals", "query-meal-detail",
    "calculate-price", "create-order", "query-order", "cancel-order",
]


def test_skill_frontmatter():
    s = read("lanlanlu/SKILL.md")
    assert s.startswith("---\nname: lanlanlu\n")
    assert "\ndescription: " in s.split("---")[1]


def test_skill_mentions_every_tool():
    s = read("lanlanlu/SKILL.md")
    for tool in TOOLS_USED:
        assert f"`{tool}`" in s, tool


def test_skill_core_rules():
    s = read("lanlanlu/SKILL.md")
    for key in ["纯净区", "自检：100% 正常", "/uninstall", "references/commands.md",
                "references/endings.md", "references/climax.md"]:
        assert key in s, key


def test_skill_only_mentions_order_list_to_forbid_it():
    for line in read("lanlanlu/SKILL.md").splitlines():
        if "order-list" in line:
            assert "不调用" in line


def test_commands_cover_spec_table():
    s = read("lanlanlu/references/commands.md")
    for cmd in ["`ps`", "`top`", "`kill -9 lanlanlu.exe`", "`sudo 正常`", "`ping lanlanlu`",
                "`git blame`", "`--version`", "`help`", "`↑↑↓↓←→←→BA`", "`上上下下左右左右BA`",
                "`/uninstall`", "`/lanlanlu`"]:
        assert cmd in s, cmd


def test_endings_scripts():
    s = read("lanlanlu/references/endings.md")
    for key in ["结局 1/5 已解锁：《假性修复》", "结局 3/5 已解锁：《反向污染》",
                "[WARN] 报告审核人数：2", "检测到用户已被污染", "references/climax.md"]:
        assert key in s, key


def test_climax_points_to_frames_and_player():
    s = read("lanlanlu/references/climax.md")
    assert "references/climax-frames.md" in s
    assert "python player/play.py" in s


def test_mcp_integration_lists_every_tool():
    s = read("MCP_INTEGRATION.md")
    assert "https://mcp.mcd.cn" in s
    for tool in TOOLS_USED:
        assert f"`{tool}`" in s, tool
