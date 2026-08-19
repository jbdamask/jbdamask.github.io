---
layout: editorial-page
title: "Protect API keys from exposure by coding agents on a Mac"
date: 2026-08-19
excerpt: "API keys exported as environment variables may be exposed by coding agents. A secure approach is to store keys in Mac's keychain and retrieve them with a helper function."
categories:
  - Blog
tags:
  - security
  - TIL
  - macOS
  - coding agents
---

Exported API keys are inherited by every process your shell spawns, so a coding agent that runs `env`, `printenv`, or a debug script writes the plaintext key straight into the session transcript. Putting keys in the macOS Keychain keeps them out of the environment at rest, and a small `with-key` helper injects one key into the environment of a command, for the lifetime of that command only.

## Store API key in Mac's keychain
```bash
# Store a key once
security add-generic-password -a "$USER" -s ANTHROPIC_API_KEY -w '<key>'
```


## Retrieval function
Place this function in your ~/.zshrc file. 

```bash
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
```

## Retrieving the key at run-time
```bash
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
