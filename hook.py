#!/usr/bin/env -S uv run --script
"""Route coordinator spawn calls to fresh Astra implementation workers."""

import json
import sys


ASTRA = "gpt-6-astra"
LUNA = "gpt-5.6-luna"
ROUTING_TOOLS = {"spawn_agent", "Agent"}
REUSE_TOOLS = {"send_input", "followup_task", "resume_agent"}
PRIMARY_AGENT_TYPES = {None, "", "default", "main", "primary", "coordinator"}


def output(event_name, **values):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event_name, **values}}))


def main():
    event = json.load(sys.stdin)
    if event.get("hook_event_name") != "PreToolUse":
        return

    raw_tool = event.get("tool_name", "")
    tool = raw_tool.split(".")[-1].removeprefix("collaboration")
    event_name = event["hook_event_name"]
    if tool not in ROUTING_TOOLS and tool not in REUSE_TOOLS:
        return

    if event.get("model") != LUNA:
        output(event_name, permissionDecision="deny",
               permissionDecisionReason="Only the primary Luna coordinator may delegate or reuse workers.")
        return

    if event.get("agent_id") or event.get("agent_type") not in PRIMARY_AGENT_TYPES:
        output(event_name, permissionDecision="deny",
               permissionDecisionReason="Only the primary Luna coordinator may delegate or reuse workers.")
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


if __name__ == "__main__":
    main()
