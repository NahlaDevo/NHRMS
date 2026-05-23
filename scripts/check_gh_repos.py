import json, sys
repos = json.loads(sys.stdin.read())
for r in repos:
    print(f'{r["name"]:30} private={r["private"]}  url={r["html_url"]}')
