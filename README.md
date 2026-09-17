# Lunastra

Luna drives the task; Astra writes production code. You talk to one Codex session.

| Role | Model / effort | Owns |
| --- | --- | --- |
| Coordinator | `gpt-5.6-luna` / `xhigh` | Planning, tests, review, validation, Git |
| Implementation worker | `gpt-6-astra` / `high` | One bounded production change |

Each implementation or repair gets a fresh Astra worker without the parent chat
history. Astra reports its changes; Luna reviews them and runs the checks.

## Setup

Install [Codex CLI](https://developers.openai.com/codex/cli),
[uv](https://docs.astral.sh/uv/getting-started/installation/), and Git. Your Codex
account needs access to both models. Shell examples use Bash or zsh on macOS/Linux.
On macOS with Homebrew:

```sh
brew install --cask codex
brew install uv git
```

Clone the repo and copy its configuration into a dedicated Codex home. This keeps
your normal Codex configuration untouched; existing skills, plugins, and MCP
settings are not copied.

```sh
git clone https://github.com/MaksimMisin/lunastra.git "$HOME/code/lunastra"
export LUNASTRA_HOME="$HOME/code/lunastra"
mkdir -p "$HOME/.codex-lunastra"
cp -i "$LUNASTRA_HOME/config.toml" "$LUNASTRA_HOME/astra.toml" \
  "$LUNASTRA_HOME/hooks.json" "$HOME/.codex-lunastra/"
```

Add these shortcuts to `~/.zshrc` or `~/.bashrc`, then reload that file:

```sh
export LUNASTRA_HOME="$HOME/code/lunastra"

lunastra() {
  CODEX_HOME="$HOME/.codex-lunastra" command codex "$@"
}
alias lu='lunastra'
alias lur='lunastra resume'
alias lul='lunastra resume --last'
```

`LUNASTRA_HOME` points to the clone; `CODEX_HOME` selects Codex's configuration
and session storage. If you cloned elsewhere, change `LUNASTRA_HOME` in both places.
The function expects the official `codex` executable on `PATH`; if you have a
wrapper there, replace `command codex` with the official binary's absolute path.

Sign in for this Codex home, then launch from the project you want to change:

```sh
lunastra login
cd /path/to/your/project
lu
```

On first launch, open `/hooks`, review the Lunastra `PreToolUse` command, and trust
it. **Untrusted hooks are skipped.** Use `/status` to check Luna and its effort;
use `/agent` to inspect Astra workers once implementation starts. Keep the configured
models during the session.

To use an existing Codex home instead, merge the settings from `config.toml` and
the hook entry into your existing files, and copy `astra.toml` beside that
`config.toml`. Preserve your other settings and hook entries.

## Daily use

```sh
lu                         # new session in the current project
lu "Add pagination to the users endpoint and test the boundary cases."
lur                        # choose a previous session
lul                        # resume the latest session in this directory
lur --all                  # find sessions from other directories
lunastra resume SESSION_ID # resume a specific session
```

Give Luna the task, constraints, and acceptance criteria. It handles delegation;
you do not launch Astra yourself. For bugs, ask for a reproducing test first.
Luna owns tests and Markdown/docs; Astra owns production edits. Common test paths
such as `tests/`, `__tests__/`, `test_*.py`, `*.test.*`, and `*.spec.*` are recognized
by [hook.py](hook.py).

Start new Lunastra tasks with `lu`; use the resume shortcuts for sessions already
started with this setup. The standalone configuration does not replace policy
instructions saved in older conversations.

## My everyday shortcuts

My private dotfiles provide account-specific launchers. Work accounts and their
launcher names are anonymized here as `work1` and `work2`:

```sh
codex                      # Lunastra; work1, or work2 inside its project folder
codexp                     # Lunastra; personal account
codex-work1                # Lunastra; work1 account
codex-work2                # Lunastra; work2 account
codex resume --last        # continue work
codexs                     # plain Astra, medium effort
codexl                     # plain Astra, max effort
codex-work2l               # plain Astra, max effort, work2 account
codexpxl --lunastra         # personal; force Luna xhigh + Astra high
codexs --selective-lunastra # Luna handles routine edits; Astra gets complex work
```

The suffixes `xs`, `s`, `m`, `l`, `xl` select plain Astra at `low`, `medium`,
`high`, `max`, `ultra`; they also work after `codexp`, `codex-work1`, and
`codex-work2`. Unsuffixed commands default to Lunastra. An explicit mode flag
overrides the alias's model and effort.

**These account launchers and mode flags belong to the dotfiles wrapper.**
This repo supplies the standalone configuration and hook; use `lu` above without
installing my dotfiles. The wrapper additionally handles selective mode,
`.codex/lunastra.json` ownership policies, launch checks, audit logs, and policy
refresh on resume. Those features are not included here.

## Updates and troubleshooting

Update the clone with `git -C "$LUNASTRA_HOME" pull --ff-only`, repeat the copy
command above, then exit and relaunch. Merge configuration changes if you customized
your copies. Check `/hooks` again after updates.

| Symptom | Check |
| --- | --- |
| No hook enforcement | Open `/hooks`; ensure the Lunastra hook is enabled and trusted. |
| `uv` or `hook.py` not found | Check `command -v uv` and `LUNASTRA_HOME` in the launching shell. |
| Wrong model or missing worker instructions | Check the active Codex home, all three copied files, and project config overrides. |
| `--lunastra` is rejected | That flag needs the dotfiles wrapper; the standalone shortcut is `lu`. |
| An edit is denied | Check the file's test/production ownership; start from the project root. The standalone hook rejects outside-workspace and symlink-traversing patches. |

The hook controls delegation and patch ownership. Shell access still uses Codex's
normal permissions; this is a workflow guardrail, not a sandbox.

Files: [config.toml](config.toml) selects the coordinator and registers the worker;
[astra.toml](astra.toml) defines its instructions; [hooks.json](hooks.json) runs
[hook.py](hook.py). Codex references:
[CLI commands](https://developers.openai.com/codex/cli/reference),
[hook trust](https://learn.chatgpt.com/docs/hooks#review-and-trust-hooks).

Benchmark setup and evidence rules: [BENCHMARKS.md](BENCHMARKS.md).
