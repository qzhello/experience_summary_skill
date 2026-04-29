#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CLAUDE_ROOT="${HOME}/.claude"
CLAUDE_SKILL_DIR="${CLAUDE_ROOT}/skills/experience-summary"
CLAUDE_COMMANDS_DIR="${CLAUDE_ROOT}/commands"
CLAUDE_COMMAND_FILE="${CLAUDE_COMMANDS_DIR}/exp.md"

CODEX_ROOT="${HOME}/.codex"
CODEX_SKILL_DIR="${CODEX_ROOT}/skills/experience-summary"
CODEX_ALIAS_DIR="${CODEX_ROOT}/skills/exp"
CODEX_ALIAS_FILE="${CODEX_ALIAS_DIR}/SKILL.md"

INSTALL_CLAUDE=0
INSTALL_CODEX=0
GLOBAL_MODE=0
PULL_MODE=0

usage() {
  cat <<'EOF'
Usage:
  ./install.sh
  ./install.sh -g
  ./install.sh --pull
  ./install.sh --pull -g
  ./install.sh --claude
  ./install.sh --codex
  ./install.sh -h

Modes:
  (no args)   Interactive install. If both ~/.claude and ~/.codex exist, ask which to install.
  -g          Install/update everything that exists locally. No prompt.
  --pull      Run `git pull --ff-only` first, then install.
  --claude    Install/update Claude Code only.
  --codex     Install/update Codex only.
  -h          Show help.
EOF
}

git_pull_if_requested() {
  if [[ "$PULL_MODE" -ne 1 ]]; then
    return 0
  fi

  if [[ ! -d "$SCRIPT_DIR/.git" ]]; then
    echo "[error] --pull requested, but current directory is not a git repository."
    exit 1
  fi

  if ! git -C "$SCRIPT_DIR" remote get-url origin >/dev/null 2>&1; then
    echo "[error] --pull requested, but git remote 'origin' is not configured."
    exit 1
  fi

  echo "[info] Running git pull --ff-only ..."
  git -C "$SCRIPT_DIR" pull --ff-only
}

copy_dir() {
  local src="$1"
  local dst="$2"
  mkdir -p "$(dirname "$dst")"
  rm -rf "$dst"
  mkdir -p "$dst"
  cp -R "$src"/. "$dst"/
}

copy_file() {
  local src="$1"
  local dst="$2"
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
}

install_claude() {
  if [[ ! -d "$CLAUDE_ROOT" ]]; then
    echo "[skip] Claude Code not detected: $CLAUDE_ROOT"
    return 0
  fi

  copy_dir "$SCRIPT_DIR" "$CLAUDE_SKILL_DIR"
  copy_file "$SCRIPT_DIR/commands/exp.md" "$CLAUDE_COMMAND_FILE"

  echo "[ok] Claude Code"
  echo "     skill   -> $CLAUDE_SKILL_DIR"
  echo "     command -> $CLAUDE_COMMAND_FILE"
}

install_codex() {
  if [[ ! -d "$CODEX_ROOT" ]]; then
    echo "[skip] Codex not detected: $CODEX_ROOT"
    return 0
  fi

  copy_dir "$SCRIPT_DIR" "$CODEX_SKILL_DIR"
  mkdir -p "$CODEX_ALIAS_DIR"
  copy_file "$SCRIPT_DIR/aliases/exp/SKILL.md" "$CODEX_ALIAS_FILE"

  echo "[ok] Codex"
  echo "     skill -> $CODEX_SKILL_DIR"
  echo "     alias -> $CODEX_ALIAS_FILE"
}

interactive_select() {
  local has_claude=0
  local has_codex=0

  [[ -d "$CLAUDE_ROOT" ]] && has_claude=1
  [[ -d "$CODEX_ROOT" ]] && has_codex=1

  if [[ "$has_claude" -eq 0 && "$has_codex" -eq 0 ]]; then
    echo "No supported target detected."
    echo "Expected one of:"
    echo "  $CLAUDE_ROOT"
    echo "  $CODEX_ROOT"
    exit 1
  fi

  if [[ "$has_claude" -eq 1 && "$has_codex" -eq 0 ]]; then
    INSTALL_CLAUDE=1
    echo "Detected Claude Code only. Installing there."
    return
  fi

  if [[ "$has_claude" -eq 0 && "$has_codex" -eq 1 ]]; then
    INSTALL_CODEX=1
    echo "Detected Codex only. Installing there."
    return
  fi

  echo "Detected both Claude Code and Codex."
  echo "Choose install target:"
  echo "  1) Claude Code"
  echo "  2) Codex"
  echo "  3) Both"
  printf "> "
  read -r choice

  case "$choice" in
    1)
      INSTALL_CLAUDE=1
      ;;
    2)
      INSTALL_CODEX=1
      ;;
    3)
      INSTALL_CLAUDE=1
      INSTALL_CODEX=1
      ;;
    *)
      echo "Invalid choice: $choice"
      exit 1
      ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -g)
      GLOBAL_MODE=1
      INSTALL_CLAUDE=1
      INSTALL_CODEX=1
      shift
      ;;
    --pull)
      PULL_MODE=1
      shift
      ;;
    --claude)
      INSTALL_CLAUDE=1
      shift
      ;;
    --codex)
      INSTALL_CODEX=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      echo
      usage
      exit 1
      ;;
  esac
done

git_pull_if_requested

if [[ "$GLOBAL_MODE" -eq 0 && "$INSTALL_CLAUDE" -eq 0 && "$INSTALL_CODEX" -eq 0 ]]; then
  interactive_select
fi

if [[ "$INSTALL_CLAUDE" -eq 1 ]]; then
  install_claude
fi

if [[ "$INSTALL_CODEX" -eq 1 ]]; then
  install_codex
fi

if [[ "$GLOBAL_MODE" -eq 1 ]]; then
  echo "[done] Global update mode finished."
else
  echo "[done] Install finished."
fi
