import json, sys
d = json.loads(sys.stdin.read())
print(f"Login: {d.get('login')}")
print(f"Scopes from header would tell us more")
