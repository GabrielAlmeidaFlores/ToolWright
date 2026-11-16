"""
String constants for the optional session usage ledger.
"""
from __future__ import annotations

from .constants import (
    EMPTY_STRING,
    KEY_AGENT,
    KEY_APPLIED,
    KEY_COMMIT,
    KEY_COST,
    KEY_ENTRIES,
    KEY_MODEL,
    KEY_OUTPUT,
    KEY_VERIFICATION_EXIT,
)
from .constants import KEY_TASK
from .constants import TEXT_TEXT_3_3 as TEXT_CURRENT_DIR
KEY_SESSION = 'session'
from .governance_strings import KEY_RECORD as COMMAND_RECORD
from .pilot_strings import FLAG_MODEL
from .process_strings import TEXT_COMMAND_NOT_FOUND
from .verify_strings import KEY_TOTAL
from .verify_strings import TEXT_TEXT as TEXT_PARENT_DIR
from .stats_strings import (
    KEY_INPUT,
    KEY_ARM,
    KEY_WALL_SECONDS,
    KEY_WORKING_DIRECTORY,
    KEY_REASONING,
    KEY_RUN_ID,
    KEY_RUNS,
    KEY_TASK_ID,
    KEY_VERIFIED,
)

KEY_USAGE = 'usage'
KEY_USAGE_COMMAND = 'usage_command'
KEY_REWORK = 'rework'
KEY_OLDER_THAN_DAYS = 'older_than_days'
KEY_USAGE_DIR = '.toolwright/usage'
KEY_PROMPTS = 'prompts'
COMMAND_REPORT = 'report'
FLAG_SESSION = '--session'
FLAG_REWORK = '--rework'
FLAG_OLDER_THAN_DAYS = '--older-than-days'
FLAG_TIMEOUT = '--timeout'
FLAG_COMMAND = '--'
TEXT_RECORD_ONE_SESSION = 'Record one AI session into .toolwright/usage'
TEXT_REPORT_USAGE = 'Report task-level usage from .toolwright/usage'
TEXT_PRUNE_USAGE = 'Delete usage entries older than a number of days'
TEXT_SESSION_JSONL_TO_RECORD = 'Pre-captured session JSONL to record'
TEXT_TASK_NAME_FOR_USAGE = 'Task or label for the session'
TEXT_OPTIONAL_VERIFICATION_COMMAND = 'Verification command run after the wrapper command'
TEXT_OPTIONAL_REWORK_COUNT = 'Rework cycles for this session'
TEXT_OPTIONAL_RUN_ID = 'Run directory name; defaults to a timestamp'
TEXT_OPTIONAL_TIMEOUT = 'Wrapper command timeout in seconds'
TEXT_USAGE_OLD_DAYS = 'Delete entries older than this many days'
TEXT_USAGE_PRUNE_APPLY = 'Delete matching entries; without it, print the plan'
TEXT_USAGE_PRUNE_YES = 'Confirm deletion'
TEXT_RECORDED = 'recorded {} at {}'
TEXT_REPORT_HEADER = 'task | agent | model | runs | verified | cost_usd | input | output | reasoning | rework'
TEXT_REPORT_RULE = '--- | --- | --- | --- | --- | --- | --- | --- | --- | ---'
TEXT_REPORT_ROW = '{} | {} | {} | {} | {} | {:.6f} | {} | {} | {} | {}'
TEXT_PRUNE_PLAN = '{} entries older than {} days'
TEXT_PRUNE_APPLIED = 'deleted {} entries'
TEXT_PRUNE_YES_REQUIRED = 'refusing to delete usage entries without --yes'
TEXT_NEED_SESSION_OR_COMMAND = 'provide --session FILE or a command after --'
TEXT_CANNOT_USE_BOTH = 'provide either --session or a command, not both'
TEXT_USAGE_DIR_MISSING = 'no usage directory at {}'

FLAG_TASK = '--task'
FLAG_RUN_ID = '--run-id'

KEY_COMMAND_ARGS = 'command_args'
KEY_RUN_EXIT = 'run_exit'
TEXT_USAGE_EXISTS = '{} already exists'
TEXT_USAGE_META_GLOB = '*/meta.json'
TEXT_TIMEOUT_AFTER = 'timeout after {}s'
TEXT_VERIFICATION_EXIT_LINE = 'verification exit code: {}'
TEXT_SESSION_NOT_FOUND = 'session file not found: {}'
TEXT_INVALID_RUN_ID = 'run id must be a single path segment: {}'
TEXT_VERIFICATION_TIMEOUT = 'verification timed out after {}s'
KEY_PRUNED = 'pruned'
TEXT_WRITE_READ_MODE = 'w+'
TEXT_SESSION_INVALID = 'session output is not JSONL; use a command with --format json or pass --session: {}'
TEXT_WINDOWS_OS = 'nt'
TEXT_KILLPG = 'killpg'
TEXT_SIGKILL = 'SIGKILL'
