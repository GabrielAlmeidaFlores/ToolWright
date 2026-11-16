"""
Unit tests for the local usage ledger.

Public API: none. The module is a unittest test case.

Side effects: writes only inside temporary directories.
"""
from __future__ import annotations

from tests.constants import KEY_COORDINATOR, KEY_TRUE, TEXT_MAIN, TEXT_UTF_8
from tests import support
from toolwright_cli.cli import main
from toolwright_cli.cli.cli_strings import FLAG_JSON
from toolwright_cli.constants import FLAG_TARGET

import contextlib
import io
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

from toolwright_cli import usage
from toolwright_cli.paths import ToolWrightError
from toolwright_cli.constants import TEXT_SESSION_JSONL
from toolwright_cli.usage_strings import (
    COMMAND_REPORT,
    KEY_AGENT,
    KEY_MODEL,
    KEY_USAGE,
    KEY_VERIFICATION_EXIT,
    COMMAND_REPORT,
    KEY_COST,
    KEY_REWORK,
    KEY_ENTRIES,
    KEY_RUNS,
    KEY_TOTAL,
    KEY_TASK,
    KEY_VERIFIED,
)

TEXT_TEST_TASK = 'usage-test-task'
TEXT_TEST_MODEL = 'test/model'
TEXT_JSON_PRINT = 'import json; print(json.dumps({"type": "step_finish", "part": {"cost": 0.5, "tokens": {"input": 10, "output": 2, "reasoning": 1, "cache": {"read": 0, "write": 0}}}}))'
TEXT_FALSE = 'false'
OLD_AGE_SECONDS = 3650 * 86400
DAY_SECONDS = 86400
TEXT_FUTURE_DAYS = '90'
TEXT_EMIT_SCRIPT = 'emit_usage.py'
TEXT_ESCAPED_RUN_ID = '../usage-escape'
TEXT_ESCAPE_BASENAME = 'usage-escape'
TEXT_NOT_JSON = 'not-json'
TEXT_NOT_JSON_SCRIPT = 'print("not-json")'
TEXT_FAIL_JSON_SCRIPT = 'import json, sys; print(json.dumps({"type": "step_finish", "part": {"cost": 0.1}})); sys.exit(1)'
TEXT_SESSION_EVENT = '{"type": "step_finish", "part": {"cost": 0.25, "tokens": {"input": 100, "output": 20, "reasoning": 5, "cache": {"read": 40, "write": 0}}}}\n'
TEXT_OLD_ENTRY = 'usage-old-entry'
TEXT_RUN_ONE = 'usage-run-1'
TEXT_RUN_TWO = 'usage-run-2'


class UsageRecordTests(unittest.TestCase):

    def test_records_session_and_reports_task(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            session = target / TEXT_SESSION_JSONL
            session.write_text(TEXT_SESSION_EVENT, encoding=TEXT_UTF_8)
            meta = usage.record_usage(
                target,
                task=TEXT_TEST_TASK,
                session=session,
                verify=KEY_TRUE,
                agent=KEY_COORDINATOR,
                model=TEXT_TEST_MODEL,
                rework=1,
                run_id=TEXT_RUN_ONE,
            )
            self.assertEqual(meta[KEY_REWORK], 1)
            self.assertTrue((usage.usage_root(target) / TEXT_RUN_ONE / TEXT_SESSION_JSONL).is_file())
            payload = usage.report_payload(target)
            self.assertEqual(len(payload[KEY_ENTRIES]), 1)
            entry = payload[KEY_ENTRIES][0]
            self.assertEqual(entry[KEY_TASK], TEXT_TEST_TASK)
            self.assertEqual(entry[KEY_AGENT], KEY_COORDINATOR)
            self.assertEqual(entry[KEY_MODEL], TEXT_TEST_MODEL)
            self.assertEqual(entry[KEY_REWORK], 1)
            self.assertEqual(entry[KEY_VERIFIED], 1)

    def test_session_roundtrip_without_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            session = target / TEXT_SESSION_JSONL
            session.write_text(TEXT_SESSION_EVENT, encoding=TEXT_UTF_8)
            usage.record_usage(
                target,
                task=TEXT_TEST_TASK,
                session=session,
                run_id=TEXT_RUN_ONE,
            )
            entry = usage.report_payload(target)[KEY_ENTRIES][0]
            self.assertEqual(entry[KEY_VERIFIED], 0)
            self.assertTrue((usage.usage_root(target) / TEXT_RUN_ONE / TEXT_SESSION_JSONL).is_file())

    def test_wrapper_records_command_and_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            script = target / TEXT_EMIT_SCRIPT
            script.write_text(TEXT_JSON_PRINT, encoding=TEXT_UTF_8)
            meta = usage.record_usage(
                target,
                task=TEXT_TEST_TASK,
                command=[sys.executable, str(script)],
                verify=KEY_TRUE,
                agent=KEY_COORDINATOR,
                model=TEXT_TEST_MODEL,
                run_id=TEXT_RUN_TWO,
            )
            self.assertEqual(meta[KEY_VERIFICATION_EXIT], 0)
            self.assertTrue((usage.usage_root(target) / TEXT_RUN_TWO / TEXT_SESSION_JSONL).is_file())

    def test_cli_report_dispatches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            script = target / TEXT_EMIT_SCRIPT
            script.write_text(TEXT_JSON_PRINT, encoding=TEXT_UTF_8)
            usage.record_usage(target, task=TEXT_TEST_TASK, command=[sys.executable, str(script)], run_id=TEXT_RUN_ONE)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = main([KEY_USAGE, COMMAND_REPORT, FLAG_TARGET, str(target), FLAG_JSON])
            self.assertEqual(code, 0)
            payload = json.loads(buffer.getvalue())
            self.assertEqual(payload[KEY_TOTAL], 1)

    def test_rejects_non_jsonl_session(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            session = target / TEXT_SESSION_JSONL
            session.write_text(TEXT_NOT_JSON + '\n', encoding=TEXT_UTF_8)
            with self.assertRaises(ToolWrightError):
                usage.record_usage(target, task=TEXT_TEST_TASK, session=session, run_id=TEXT_RUN_ONE)

    def test_rejects_non_jsonl_command_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            script = target / TEXT_EMIT_SCRIPT
            script.write_text(TEXT_NOT_JSON_SCRIPT, encoding=TEXT_UTF_8)
            with self.assertRaises(ToolWrightError):
                usage.record_usage(target, task=TEXT_TEST_TASK, command=[sys.executable, str(script)], run_id=TEXT_RUN_ONE)

    def test_rejects_path_traversal_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            with self.assertRaises(ToolWrightError):
                usage.record_usage(target, task=TEXT_TEST_TASK, command=[KEY_TRUE], run_id=TEXT_ESCAPED_RUN_ID)
            self.assertFalse((usage.usage_root(target).parent / TEXT_ESCAPE_BASENAME).exists())

    def test_failed_wrapper_is_not_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            script = target / TEXT_EMIT_SCRIPT
            script.write_text(TEXT_FAIL_JSON_SCRIPT, encoding=TEXT_UTF_8)
            usage.record_usage(
                target,
                task=TEXT_TEST_TASK,
                command=[sys.executable, str(script)],
                verify=KEY_TRUE,
                run_id=TEXT_RUN_TWO,
            )
            entry = usage.report_payload(target)[KEY_ENTRIES][0]
            self.assertEqual(entry[KEY_VERIFIED], 0)

    def test_prune_requires_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            entry = usage.usage_root(target) / TEXT_OLD_ENTRY
            entry.mkdir(parents=True)
            os.utime(entry, (time.time() - OLD_AGE_SECONDS, time.time() - OLD_AGE_SECONDS))
            with self.assertRaises(Exception):
                usage.prune_usage(target, older_than_days=int(TEXT_FUTURE_DAYS), apply=True, yes=False)
            candidates, applied = usage.prune_usage(target, older_than_days=int(TEXT_FUTURE_DAYS), apply=True, yes=True)
            self.assertEqual(candidates, [TEXT_OLD_ENTRY])
            self.assertTrue(applied)
            self.assertFalse(entry.exists())


if __name__ == TEXT_MAIN:
    unittest.main()
