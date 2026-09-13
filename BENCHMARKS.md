# Lunastra benchmarks

Keep the benchmark harness and raw runs outside this repository. This repo
should contain the routing policy and the short experiment contract only.

## Before the run

1. Pin one public repository commit and one task file. Record both hashes,
   repository metadata, the installed Codex version, and the randomized attempt
   order.
2. Run the untouched baseline first. Save its normal-check results and require
   a passing baseline for any hidden-oracle comparison.
3. Build one immutable image with public dependencies and the baseline checkout.
   Do not bake in a candidate patch, hidden tests, notes, transcripts, or
   controller credentials.

## Attempt isolation

Give every attempt a new container, checkout, home, `CODEX_HOME`, SQLite store,
temporary directory, writable cache, and internal network. Mount nothing from
the host: no worktree, Docker socket, SSH keys, account state, notes, prior
sessions, or benchmark results. Copy only the per-run authentication identity
into the fresh private home.

Use a disposable egress gateway per attempt. Attach it to that attempt's
private network and an Internet-facing network, but publish no gateway port.
Allow only the exact inference, model-catalog, quota, compaction, and OAuth
routes required by the native CLI. Pin hosts and methods, reject redirects and
unobserved response IDs, and filter request/response payloads. The contestant
gets only the gateway CA certificate.

The contestant should have no effective, permitted, or bounding Linux
capabilities, no host namespaces, and no privilege escalation path. Firewall
egress to the gateway and loopback only; block DNS, host services, public sites,
history APIs, MCP, hosted tools, and remote files. Verify these facts before
the model starts and record the container configuration. This is Docker/process
isolation, not a kernel-escape guarantee; the inference service and account
quota remain shared external dependencies.

## Run and audit

Use the native Codex binary with a fresh config. Disable memories, plugins,
apps, hosted integrations, and web search unless the experiment explicitly
measures one of them. Keep the task bytes, time limit, environment, and
validation commands identical across modes. Do not provide hints or repair an
attempt after launch.

For hybrid Lunastra runs, preflight and record:

- Luna `gpt-5.6-luna` at xhigh and fresh Astra `gpt-6-astra` workers at high;
- the exact hook registration, enabled/trusted state, and applied routing;
- private home/SQLite state, symlink containment, capabilities, network proof,
  and absence of inherited sessions;
- native rollout metadata, hook decisions, changed paths, and command results.

Requested delegation and model self-reports are not proof. Pair hook records
with native transcripts and result evidence. Review shell ownership separately:
the hook is a guardrail, not an operating-system enforcement boundary.

## Evaluation and review

Evaluate each frozen checkout in a separate fresh container. Keep hidden tests,
the oracle, evaluator source, and evaluator output out of the contestant image.
Prove the oracle against the untouched baseline, then run every candidate with
the same evaluator. Never return hidden-test diagnostics to a contestant.

Review the exact submitted diff for real behavior, retained tests, ownership and
layering, security boundaries, no-op/cosmetic work, unrelated changes, and
over-engineering. Passing repository checks is a release gate, not a quality
ranking. Record inherited baseline failures separately from candidate failures.

Account for tokens from unique per-response usage records. Treat missing usage
as unknown, not zero. Record complete attempt wall time separately from setup
and export overhead, and take settling quota observations when the provider
reports only coarse percentages.

## Minimal run shape

Keep the controller private, but make its stages explicit:

```text
freeze source/task
  -> build immutable public-dependency image
  -> baseline checks + oracle proof
  -> preflight each fresh isolated attempt
  -> run attempts in recorded random order
  -> export sanitized artifacts
  -> evaluate frozen patches in fresh evaluator containers
  -> audit routing/isolation/usage
  -> review diffs and publish a limitations-aware table
```

At minimum, retain per attempt: source/task hashes, image identity, isolation
proof, preflight result, process state, sanitized native logs, hook audit,
tokens/quota observations, submitted diff, check results, oracle result, and
review flags. Keep credentials, raw auth state, and unreviewed session data in
private controller storage only.
