#!/usr/bin/env python3
"""클라우드 작업대의 그 자리에 답을 붙인다.

  python3 tools/답하기.py "box:amt" "고쳤습니다 …"
"""
import json, sys, time, urllib.request, urllib.parse

KEY  = "AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"
PROJ = "vivivic-4b7ef"
뿌리  = f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"


def 토큰():
    r = urllib.request.urlopen(urllib.request.Request(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
        json.dumps({"returnSecureToken": True}).encode(), {"Content-Type": "application/json"}))
    return json.load(r)["idToken"]


def 풀기(v):
    k = next(iter(v))
    if k == "arrayValue": return [풀기(x) for x in v[k].get("values", [])]
    if k == "mapValue":   return {a: 풀기(b) for a, b in v[k].get("fields", {}).items()}
    if k == "integerValue": return int(v[k])
    if k == "nullValue":  return None
    return v[k]


def 값(v):
    if v is None: return {"nullValue": None}
    if isinstance(v, bool): return {"booleanValue": v}
    if isinstance(v, int): return {"integerValue": str(v)}
    if isinstance(v, str): return {"stringValue": v}
    if isinstance(v, list): return {"arrayValue": {"values": [값(x) for x in v]}}
    if isinstance(v, dict): return {"mapValue": {"fields": {k: 값(x) for k, x in v.items()}}}
    return {"stringValue": str(v)}


자리, 글 = sys.argv[1], sys.argv[2]
tok = 토큰()
did = urllib.parse.quote(자리).replace("%", "~")
url = f"{뿌리}/wt_dev/{did}"
try:
    d = json.load(urllib.request.urlopen(urllib.request.Request(
        url, headers={"Authorization": "Bearer " + tok})))
    f = {k: 풀기(v) for k, v in d["fields"].items()}
except Exception:
    f = {"area": 자리, "msgs": []}
f.setdefault("msgs", []).append({"who": "클로드", "text": 글, "at": int(time.time())})
f["area"] = 자리
f["잰때"] = int(time.time() * 1000)
body = json.dumps({"fields": {k: 값(v) for k, v in f.items()}}).encode()
urllib.request.urlopen(urllib.request.Request(
    url, body, {"Authorization": "Bearer " + tok, "Content-Type": "application/json"},
    method="PATCH")).read()
print(f"답 붙임 · {자리} · 말 {len(f['msgs'])}개")
