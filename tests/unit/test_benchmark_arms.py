"""
Unit tests for benchmark-only arm configuration.

Public API: none. The module is a unittest test case.

Side effects: reads benchmark arm configs only.
"""
from __future__ import annotations

from tests.constants import KEY_AGENTS, KEY_COORDINATOR, KEY_OPENCODE, TEXT_MAIN, TEXT_OPENCODE_JSONC, TEXT_UTF_8

import json
import unittest

from tests import support

KEY_DEFAULT_AGENT = 'default_agent'
KEY_MAX_LINES = 'max_lines'
KEY_MCP = 'mcp'
KEY_SERVERS = 'servers'
KEY_TOOL_OUTPUT = 'tool_output'
TEXT_ARMS = 'arms'
TEXT_SCOPED_ROUTER_FILE = 'scoped-router.md'
TEXT_SCOPED_ROUTER_DESCRIPTION = 'Benchmark-only scoped router'
TEXT_ACTION_EDIT = 'action: edit'
TEXT_EFFECT_ALLOW = 'effect: allow'
TEXT_SCOPED_ROUTER_CONDITION = 'For a task confined to one known file'
TEXT_BENCHMARKS = 'benchmarks'
TEXT_CONFIGS = 'configs'
TEXT_MINIMAL_JSONC = 'minimal.jsonc'
TEXT_SLIM_JSONC = 'slim.jsonc'
TEXT_TOOLS_ON_DEMAND_JSONC = 'tools-on-demand.jsonc'
DEFAULT_TOOL_OUTPUT_LINES = 2000
BENCHMARK_ARMS = support.REPO_ROOT / TEXT_BENCHMARKS / TEXT_ARMS
SCOPED_ROUTER_AGENT = support.REPO_ROOT / TEXT_BENCHMARKS / KEY_AGENTS / TEXT_SCOPED_ROUTER_FILE
MINIMAL_CONFIG = support.REPO_ROOT / TEXT_CONFIGS / KEY_OPENCODE / TEXT_MINIMAL_JSONC
FULL_CONFIG = support.REPO_ROOT / TEXT_CONFIGS / KEY_OPENCODE / TEXT_OPENCODE_JSONC
LIMIT_TOOL_OUTPUT_LINES = 400
ARMS_WITHOUT_MCP = (TEXT_SLIM_JSONC,)
ARM_SOURCES = {
    TEXT_SLIM_JSONC: MINIMAL_CONFIG,
    TEXT_TOOLS_ON_DEMAND_JSONC: FULL_CONFIG,
}


def load_arm(name: str) -> dict:
    """
    Load one arm config with the repository JSONC parser.

    Parameters:
        name: arm config file name.

    Returns:
        Parsed JSON object.
    """
    text = (BENCHMARK_ARMS / name).read_text(encoding=TEXT_UTF_8)
    return json.loads(support.load_validator().strip_jsonc(text))


class BenchmarkArmConfigTests(unittest.TestCase):

    def test_slim_arm_disables_mcp_and_limits_tool_output(self) -> None:
        for name in ARMS_WITHOUT_MCP:
            config = load_arm(name)
            self.assertEqual(config[KEY_MCP][KEY_SERVERS], {})
            self.assertEqual(config[KEY_TOOL_OUTPUT][KEY_MAX_LINES], LIMIT_TOOL_OUTPUT_LINES)

    def test_tools_on_demand_keeps_mcp_surface(self) -> None:
        config = load_arm(TEXT_TOOLS_ON_DEMAND_JSONC)
        self.assertTrue(config[KEY_MCP][KEY_SERVERS])
        self.assertEqual(config[KEY_DEFAULT_AGENT], KEY_COORDINATOR)
        self.assertEqual(config[KEY_TOOL_OUTPUT][KEY_MAX_LINES], LIMIT_TOOL_OUTPUT_LINES)

    def test_arms_match_their_source_config_except_tool_output(self) -> None:
        for arm, source in ARM_SOURCES.items():
            arm_config = load_arm(arm)
            source_config = json.loads(
                support.load_validator().strip_jsonc(source.read_text(encoding=TEXT_UTF_8))
            )
            self.assertNotEqual(arm_config[KEY_TOOL_OUTPUT], source_config[KEY_TOOL_OUTPUT], arm)
            arm_config.pop(KEY_TOOL_OUTPUT)
            source_config.pop(KEY_TOOL_OUTPUT)
            self.assertEqual(arm_config, source_config, arm)

    def test_slim_uncapped_uses_default_output_cap(self) -> None:
        config = json.loads(
            support.load_validator().strip_jsonc(MINIMAL_CONFIG.read_text(encoding=TEXT_UTF_8))
        )
        self.assertEqual(config[KEY_MCP][KEY_SERVERS], {})
        self.assertEqual(config[KEY_TOOL_OUTPUT][KEY_MAX_LINES], DEFAULT_TOOL_OUTPUT_LINES)

    def test_scoped_router_permits_direct_edit(self) -> None:
        text = SCOPED_ROUTER_AGENT.read_text(encoding=TEXT_UTF_8)
        self.assertIn(TEXT_SCOPED_ROUTER_DESCRIPTION, text)
        self.assertIn(TEXT_ACTION_EDIT, text)
        self.assertIn(TEXT_EFFECT_ALLOW, text)
        self.assertIn(TEXT_SCOPED_ROUTER_CONDITION, text)

    def test_arms_do_not_override_agent_frontmatter(self) -> None:
        for name in (TEXT_SLIM_JSONC, TEXT_TOOLS_ON_DEMAND_JSONC):
            self.assertNotIn(KEY_AGENTS, load_arm(name), name)


if __name__ == TEXT_MAIN:
    unittest.main()
