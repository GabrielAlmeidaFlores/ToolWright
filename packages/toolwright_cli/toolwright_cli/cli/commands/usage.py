"""
Usage ledger command handler.

Public API: :func:`_command_usage`.

Side effects: writes, reports, or prunes ``.toolwright/usage`` through the usage module.
"""
from __future__ import annotations
from ..cli_strings import KEY_PRUNE as COMMAND_PRUNE
from ...constants import KEY_APPLIED
from ...usage_strings import KEY_PRUNED
from ...usage_strings import (
    EMPTY_STRING,
    FLAG_COMMAND,
    KEY_RUN_ID,
    COMMAND_RECORD,
    COMMAND_REPORT,
    TEXT_PRUNE_APPLIED,
    TEXT_PRUNE_PLAN,
    TEXT_RECORDED,
)

import argparse
from pathlib import Path

from ..common import emit_payload
from ... import usage as usage_module
from ...paths import resolve_target


def _command_usage(args: argparse.Namespace) -> int:
    target = resolve_target(args.target)
    if args.usage_command == COMMAND_RECORD:
        command = list(args.command_args or [])
        if command and command[0] == FLAG_COMMAND:
            command = command[1:]
        meta = usage_module.record_usage(
            target,
            task=args.task,
            session=Path(args.session).expanduser() if args.session else None,
            command=command or None,
            verify=args.verify,
            agent=args.agent or EMPTY_STRING,
            model=args.model or EMPTY_STRING,
            rework=args.rework,
            run_id=args.run_id,
            timeout=args.timeout,
        )
        if args.json:
            emit_payload(meta, True)
        else:
            print(TEXT_RECORDED.format(meta[KEY_RUN_ID], usage_module.usage_root(target) / meta[KEY_RUN_ID]))
        return 0
    if args.usage_command == COMMAND_REPORT:
        if args.json:
            emit_payload(usage_module.report_payload(target), True)
        else:
            print(usage_module.render_report(target), end=EMPTY_STRING)
        return 0
    if args.usage_command == COMMAND_PRUNE:
        candidates, applied = usage_module.prune_usage(
            target,
            older_than_days=args.older_than_days,
            apply=args.apply,
            yes=args.yes,
        )
        if args.json:
            emit_payload({KEY_PRUNED: candidates, KEY_APPLIED: applied}, True)
        elif applied:
            print(TEXT_PRUNE_APPLIED.format(len(candidates)))
        else:
            print(TEXT_PRUNE_PLAN.format(len(candidates), args.older_than_days))
        return 0
    return 2
