#!/usr/bin/env -S uv run --script
"""Route coordinator spawn calls to fresh Astra implementation workers."""

import json
import fnmatch
from pathlib import Path
import re
import sys


ASTRA = "gpt-6-astra"
LUNA = "gpt-5.6-luna"
ROUTING_TOOLS = {"spawn_agent", "Agent"}
REUSE_TOOLS = {"send_input", "followup_task", "resume_agent", "send_message"}
PRIMARY_AGENT_TYPES = {None, "", "default", "main", "primary", "coordinator"}
TEST_PATHS = {
    "test/*", "tests/*", "*/test/*", "*/tests/*", "*/__tests__/*",
    "__tests__/*", "test_*.py", "*/test_*.py", "*_test.py", "*_test.go",
    "*.test.*", "*.spec.*", "*Tests/*", "*Test.java",
}


def deny(event_name, reason):
    output(event_name, permissionDecision="deny",
           permissionDecisionReason=f"Lunastra: {reason}")


def patch_paths(command):
    return [path.strip() for path in re.findall(
        r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$",
        command, re.MULTILINE)]


def patch_allowed(event):
    raw_paths = patch_paths((event.get("tool_input") or {}).get("command", ""))
    if not raw_paths:
        deny(event["hook_event_name"], "patch has no recognized paths.")
        return
    cwd = Path(event.get("cwd") or ".").resolve()
    model = event.get("model")
    agent_type = event.get("agent_type")
    if model not in {LUNA, ASTRA}:
        deny(event["hook_event_name"], "unexpected model; restart with --lunastra.")
        return
    if model == LUNA and (event.get("agent_id") or agent_type not in PRIMARY_AGENT_TYPES):
        deny(event["hook_event_name"], "only the primary Luna coordinator may edit coordination files.")
        return
    for raw_path in raw_paths:
        lexical_path = cwd / raw_path
        if lexical_path.is_symlink() or any(parent.is_symlink() for parent in lexical_path.parents):
            deny(event["hook_event_name"], "patch paths may not traverse symlinks.")
            return
        path = lexical_path.resolve()
        try:
            relative = path.relative_to(cwd).as_posix()
        except ValueError:
            deny(event["hook_event_name"], "patch path is outside the current workspace.")
            return
        if path.name == "lunastra.json" and path.parent.name == ".codex":
            deny(event["hook_event_name"], "the user controls the repository policy.")
            return
        recognized_test = any(fnmatch.fnmatchcase(relative, pattern) for pattern in TEST_PATHS)
        coordination_doc = relative == "README.md" or relative.startswith("docs/") or relative.endswith(".md")
        allowed = ((model == ASTRA and not recognized_test)
                   or (model == LUNA and (recognized_test or coordination_doc)))
        if not allowed:
            deny(event["hook_event_name"],
                 "Luna edits tests/docs; Astra edits production code. Spawn a fresh Astra for production changes.")
            return


def is_primary_luna(event):
    return (event.get("model") == LUNA and not event.get("agent_id")
            and event.get("agent_type") in PRIMARY_AGENT_TYPES)


def output(event_name, **values):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event_name, **values}}))


def route(event):
    raw_tool = event.get("tool_name", "")
    tool = raw_tool.split(".")[-1].removeprefix("collaboration")
    event_name = event["hook_event_name"]
    if tool not in ROUTING_TOOLS and tool not in REUSE_TOOLS:
        return

    if not is_primary_luna(event):
        deny(event_name, "Only the primary Luna coordinator may delegate or reuse workers.")
        return

    if tool in ROUTING_TOOLS:
        updated = dict(event.get("tool_input") or {})
        updated.update(model=ASTRA, reasoning_effort="high", agent_type="astra_coder")
        if "collaboration" in raw_tool:
            updated.pop("fork_context", None)
            updated["fork_turns"] = "none"
        else:
            updated.pop("fork_turns", None)
            updated["fork_context"] = False
        output(event_name, permissionDecision="allow", updatedInput=updated)
    elif tool in REUSE_TOOLS:
        output(event_name, permissionDecision="deny",
               permissionDecisionReason="Spawn a new fresh Astra worker; do not reuse workers.")


def main():
    event = json.load(sys.stdin)
    if event.get("hook_event_name") != "PreToolUse":
        return
    raw_tool = event.get("tool_name", "")
    tool = raw_tool.split(".")[-1].removeprefix("collaboration")
    if tool == "apply_patch":
        patch_allowed(event)
    elif tool in ROUTING_TOOLS or tool in REUSE_TOOLS:
        route(event)


if __name__ == "__main__":
    main()
