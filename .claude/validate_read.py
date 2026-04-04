import sys, json

data = json.load(sys.stdin)
path = data.get("tool_input", {}).get("file_path", "")

PROTEGIDOS = [
    ".env",
    ".env.local",
    ".env.production",
    "service_role",
    "secrets",
]

for p in PROTEGIDOS:
    if p in path:
        print(json.dumps({"decision": "block", "reason": f"BLOQUEADO: archivo protegido '{path}'"}))
        sys.exit(2)

sys.exit(0)
