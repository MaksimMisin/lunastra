# Lunastra

```sh
git clone <your-lunastra-repository> ~/code/lunastra
codex_home="${CODEX_HOME:-$HOME/.codex}"
ln -sf ~/code/lunastra/config.toml "$codex_home/config.toml"
ln -sf ~/code/lunastra/hooks.json "$codex_home/hooks.json"
codex
```

Requires `uv`.
