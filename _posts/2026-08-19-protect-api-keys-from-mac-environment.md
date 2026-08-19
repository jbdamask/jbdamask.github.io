---
layout: editorial-page
title: "Your coding agent can echo $ANTHROPIC_API_KEY — use macOS Keychain"
date: 2026-08-19
excerpt: "Exported keys land in session transcripts; the Keychain plus a six-line shell function hands the key to one command and nothing else."
categories:
  - Blog
tags:
  - security
  - TIL
  - macOS
  - coding agents
---

Exported API keys are inherited by every process your shell spawns, so a coding agent that runs `env`, `printenv`, or a debug script writes the plaintext key straight into the session transcript — and from there into anything that stores transcripts. Putting keys in the macOS Keychain keeps them out of the environment at rest, and a small `with-key` helper injects one key into the environment of one command, for the lifetime of that command only.

Any secret that lives in the shell environment is readable by every child process, so scope it to the single command that needs it instead of to the whole session. Verified with a live call to the Anthropic API. Called with no arguments, `with-key` lists the stored key names; the value is still visible to the command it wraps, so this stops transcript leakage, not a hostile command.

```bash
# Store a key once
security add-generic-password -a "$USER" -s GEMINI_API_KEY -w '<key>'

# Retrieve keys by name (~/.zshrc)
with-key() {
  # No arguments: list available key names
  if [[ $# -eq 0 ]]; then
    security dump-keychain ~/Library/Keychains/login.keychain-db 2>/dev/null \
      | grep '"svce"' \
      | sed 's/.*="//; s/"$//' \
      | sort -u
    return
  fi

  local name="$1"
  shift

  local value
  value="$(security find-generic-password -a "$USER" -s "$name" -w)" || return 1

  # Key name only: print its value
  if [[ $# -eq 0 ]]; then
    echo "$value"
    return
  fi

  # Otherwise run command with key in its environment
  env "$name=$value" "$@"
}

# Use it — the key never touches the shell environment
$ curl -s https://api.anthropic.com/v1/messages \
    -H "x-api-key: $(with-key ANTHROPIC_API_KEY)" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{"model":"claude-haiku-4-5","max_tokens":100,"messages":[{"role":"user","content":"Explain how AI works in a few words"}]}' \
    | jq -r '.content[0].text'
# How AI Works (Brief)
#
# 1. **Learn from data** - AI systems are trained on large datasets to recognize patterns
# 2. **Find patterns** - They identify relationships between inputs and outputs
# 3. **Make predictions** - When given new input, they apply learned patterns to generate responses
# 4. **Improve with feedback** - Performance gets better through additional training or fine-tuning
#
# **In essence:** AI learns patterns from examples, then uses those patterns to make predictions
```
