import sys, json

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")

# Extract only the actual command, not heredoc/string content
# For git commit -m "$(cat <<'EOF' ... EOF)", only check the command verb
cmd_first_line = cmd.split("\n")[0].strip()

BLOQUEAR_CMD = [
    "rm -rf", "sudo rm", "sudo ",
    "supabase db reset", "supabase db push",
]

BLOQUEAR_EXEC = [
    "DROP TABLE", "DROP DATABASE",
]

PREGUNTAR = [
    "git push",
    "deploy",
]

# Block dangerous commands (check first line only to avoid false positives in commit messages)
for bloqueo in BLOQUEAR_CMD:
    if bloqueo.lower() in cmd_first_line.lower():
        print(json.dumps({"decision": "block", "reason": f"BLOQUEADO: comando contiene '{bloqueo}'"}))
        sys.exit(2)

# Block dangerous SQL (check full command but only if not inside git commit)
if not cmd_first_line.startswith("git commit"):
    for bloqueo in BLOQUEAR_EXEC:
        if bloqueo.lower() in cmd.lower():
            print(json.dumps({"decision": "block", "reason": f"BLOQUEADO: comando contiene '{bloqueo}'"}))
            sys.exit(2)

# Ask for permission on sensitive operations
for consulta in PREGUNTAR:
    if consulta.lower() in cmd_first_line.lower():
        print(json.dumps({"decision": "block", "reason": f"REQUIERE APROBACION: '{consulta}'. Pedi permiso al usuario."}))
        sys.exit(2)

sys.exit(0)
