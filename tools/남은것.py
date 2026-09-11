#!/usr/bin/env python3
"""아직 답 안 붙은 지시를 모두 뱉는다. 이게 비면 놓친 게 없는 것이다.

  python3 tools/남은것.py

알림은 샐 수 있다 — 감시가 끊긴 사이에 온 지시는 안 올 수도 있다.
그래서 알림을 믿지 않고 이 목록을 믿는다. 남은 것이 있으면 0 이 아닌 값으로
끝나므로, 깨어날 때마다 이것만 돌려보면 된다.

기준때 이전 것은 세지 않는다. 그 전에는 누가 언제 답했는지 표를 안 찍어서
됐는지 안 됐는지 가릴 방법이 없다. 없는 기록을 지어내지 않는다.
"""
import json, os, sys, time, urllib.request

기준때 = 1789121209          # 2026-09-11 — 여기서부터 한 건도 안 놓친다

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


tok = 토큰()
d = json.load(urllib.request.urlopen(urllib.request.Request(
    f"{뿌리}/wt_dev?pageSize=300", headers={"Authorization": "Bearer " + tok})))

남은 = []
for doc in d.get("documents", []):
    f = {k: 풀기(v) for k, v in doc["fields"].items()}
    자리 = f.get("area", "")
    for m in f.get("msgs", []):
        if m.get("who") != "나":          # 사장님 말만 센다
            continue
        때 = m.get("at", 0)
        if 때 < 기준때 or m.get("답한때"):
            continue
        남은.append((때, 자리, (m.get("text", "") or "").replace("\n", " ")))

남은.sort()
if not 남은:
    print("남은 지시 없음 — 다 답했다")
    sys.exit(0)

print(f"아직 답 안 한 지시 {len(남은)}건")
for 때, 자리, 글 in 남은:
    지난 = int((time.time() - 때) // 60)
    print(f"  {time.strftime('%m-%d %H:%M', time.localtime(때))} ({지난}분 지남) | {자리} | {글[:200]}")
sys.exit(1)
