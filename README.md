# Lunastra

Use gpt-5.6-luna at xhigh as your main driver, and gpt-6-astra at high as the code writer.

```sh
codex_home="${CODEX_HOME:-$HOME/.codex}"
ln -sf ~/code/lunastra/config.toml "$codex_home/config.toml"
ln -sf ~/code/lunastra/hooks.json "$codex_home/hooks.json"
codex
```

Requires `uv`.
