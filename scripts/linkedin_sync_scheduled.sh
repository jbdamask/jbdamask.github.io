#!/bin/zsh
# Unattended LinkedIn sync, run daily by launchd (see scripts/com.johndamask.linkedin-sync.plist).
# Runs the sync-linkedin-posts skill headlessly via Claude Code + Claude in Chrome,
# so Chrome must be open and logged into LinkedIn.

REPO="/Users/johndamask/code/jbdamask.github.io"
LOG_DIR="$HOME/Library/Logs/linkedin-sync"
LOG="$LOG_DIR/$(date +%Y-%m-%d).log"

export PATH="$HOME/.local/bin:$HOME/.rbenv/shims:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

mkdir -p "$LOG_DIR"
cd "$REPO" || exit 1

notify() {
  osascript -e "display notification \"$1\" with title \"LinkedIn sync\""
}

PROMPT='Run the /sync-linkedin-posts skill. This is an UNATTENDED scheduled run: nobody can answer questions.
- Only add posts that need no human judgment.
- Skip (do not add) any post the skill says to ask the user about: group posts duplicating a main-feed post, video/short posts with no usable text, overlaps with _data/nowigetit-posts.yml.
- If no new posts qualify, do not commit.
- If LinkedIn shows a login screen or "post cannot be displayed", stop and print "NEEDS REVIEW: LinkedIn session expired".
- End your output with a line "NEEDS REVIEW: <short list of skipped post URLs and why>" if anything was skipped, otherwise "NEEDS REVIEW: none".'

{
  echo "=== $(date) ==="
  git pull --rebase --quiet
  claude -p --chrome "$PROMPT" \
    --allowedTools "mcp__claude-in-chrome" "ToolSearch" "Skill" "Read" "Edit" "Grep" \
      "Bash(git add:*)" "Bash(git commit:*)" "Bash(git pull:*)" "Bash(git push:*)" \
      "Bash(git status:*)" "Bash(git log:*)" "Bash(git diff:*)" "Bash(ruby:*)"
  echo "exit: $?"
} >> "$LOG" 2>&1

review=$(grep -o 'NEEDS REVIEW: .*' "$LOG" | tail -1)
if [[ -z "$review" ]]; then
  notify "Run didn't finish cleanly. See $LOG"
elif [[ "$review" != "NEEDS REVIEW: none" ]]; then
  notify "${review//\"/}"
fi

# Keep 30 days of logs
find "$LOG_DIR" -name '*.log' -mtime +30 -delete
