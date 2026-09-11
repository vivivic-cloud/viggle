#!/usr/bin/env python3
"""클라우드 작업대의 그 자리에 답을 붙인다.

  python3 tools/답하기.py "box:amt" "고쳤습니다 …"
  VG_WHO=에이엠티 python3 tools/답하기.py "box:amt" "…"   ← 누가 답했는지 남는다
  python3 tools/답하기.py "box:amt" "…" --모두            ← 밀린 지시를 한 번에 답할 때

프로그램마다 작업자가 따로 있다. 예전에는 모두 '클로드' 라는 한 이름으로
답해서 누가 했는지 남지 않았다. VG_WHO 나 글 첫머리의 [○○ 작업자] 로 이름을
받아 '클로드·에이엠티' 처럼 적는다.

답은 밀린 지시 가운데 **가장 오래된 것 하나**를 맡는다(그 말에 답한때를 찍는다).
지시 셋이 오고 답 둘이 붙으면 남은 하나가 밀린 것으로 그대로 보인다 —
예전에는 자리의 마지막 말만 보아서 이런 누락이 '0건' 으로 숨었다.
"""
import json, os, re, sys, time, urllib.request, urllib.parse

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
모두 = "--모두" in sys.argv[3:]

# 누가 답하는가 — VG_WHO 가 먼저고, 없으면 글 첫머리의 [○○] 를 쓴다
누구 = (os.environ.get("VG_WHO") or "").strip()
if not 누구:
    m = re.match(r"\s*\[([^\]\n]{1,24})\]", 글)
    누구 = m.group(1).strip() if m else ""
이름 = f"클로드·{누구}" if 누구 else "클로드"

tok = 토큰()
did = urllib.parse.quote(자리).replace("%", "~")
url = f"{뿌리}/wt_dev/{did}"
try:
    d = json.load(urllib.request.urlopen(urllib.request.Request(
        url, headers={"Authorization": "Bearer " + tok})))
    f = {k: 풀기(v) for k, v in d["fields"].items()}
except Exception:
    f = {"area": 자리, "msgs": []}
지금 = int(time.time())
msgs = f.setdefault("msgs", [])

# 밀린 지시에 답한때를 찍는다. 기본은 가장 오래된 하나, --모두 면 전부.
밀린 = [m for m in msgs if m.get("who") == "나" and not m.get("답한때")]
맡은것 = 밀린 if 모두 else 밀린[:1]
for m in 맡은것:
    m["답한때"] = 지금
    m["답한이"] = 이름

# 몇 건을 맡았는지 답에도 적는다 — 읽는 쪽이 옛 방식으로 또 짝짓지 않게 하는 표다
msgs.append({"who": 이름, "text": 글, "at": 지금, "맡은수": len(맡은것)})
f["area"] = 자리
f["잰때"] = int(time.time() * 1000)
body = json.dumps({"fields": {k: 값(v) for k, v in f.items()}}).encode()
urllib.request.urlopen(urllib.request.Request(
    url, body, {"Authorization": "Bearer " + tok, "Content-Type": "application/json"},
    method="PATCH")).read()
남은 = len([m for m in f["msgs"] if m.get("who") == "나" and not m.get("답한때")])
print(f"답 붙임 · {자리} · {이름} · 맡은 지시 {len(맡은것)}건 · 아직 밀린 것 {남은}건")
