#!/usr/bin/env python3
"""클라우드 작업대에 쌓인 지시를 읽는다. 맥이 없어도 어디서나 된다.

  python3 tools/지시읽기.py             모든 자리
  python3 tools/지시읽기.py box:amt     그 박스만  ← 프로그램마다 방을 나눠 쓸 때

지시 하나하나를 센다. 예전에는 자리의 **마지막 말**만 보아서, 지시 셋이 오고
답 둘이 붙으면 남은 하나가 '0건' 으로 숨었다. 실제로 그런 누락이 있었다.
답하기.py 가 맡은 지시에 '답한때' 를 찍으므로 그것으로 가른다. 그 표가 없는
옛 말들은 순서대로 짝지어 센다(지시 N개 뒤에 답 M개면 앞의 M개만 답한 것).
"""
import json, os, sys, time, urllib.request, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 지시셈 import 밀린것

KEY  = "AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"
PROJ = "vivivic-4b7ef"
뿌리  = f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"


def 토큰():
    r = urllib.request.urlopen(urllib.request.Request(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
        json.dumps({"returnSecureToken": True}).encode(),
        {"Content-Type": "application/json"}))
    return json.load(r)["idToken"]


def 풀기(v):
    k = next(iter(v))
    if k == "arrayValue": return [풀기(x) for x in v[k].get("values", [])]
    if k == "mapValue":   return {a: 풀기(b) for a, b in v[k].get("fields", {}).items()}
    if k == "integerValue": return int(v[k])
    if k == "nullValue":  return None
    return v[k]


def 자리들(tok):
    req = urllib.request.Request(f"{뿌리}/wt_dev?pageSize=300",
                                 headers={"Authorization": "Bearer " + tok})
    d = json.load(urllib.request.urlopen(req))
    나온것 = {}
    for doc in d.get("documents", []):
        f = {k: 풀기(v) for k, v in doc["fields"].items()}
        자리 = f.get("area", "")
        if 자리:
            나온것[자리] = sorted(f.get("msgs", []), key=lambda m: m.get("at", 0))
    return 나온것


def 답한이(ms):
    for m in reversed(ms):
        if m.get("who") != "나":
            return m.get("who") or "클로드", m.get("at", 0)
    return None, 0


고를것 = sys.argv[1] if len(sys.argv) > 1 else None
모두 = 자리들(토큰())
if 고를것:
    모두 = {k: v for k, v in 모두.items() if k == 고를것}

지시수 = sum(1 for ms in 모두.values() for m in ms if m.get("who") == "나")
밀림, 묵은것 = [], []
for 자리, ms in 모두.items():
    a, b = 밀린것(ms)
    밀림 += [(m.get("at", 0), 자리, m.get("text", "")) for m in a]
    묵은것 += [(m.get("at", 0), 자리, m.get("text", "")) for m in b]
밀림.sort(); 묵은것.sort()

print((f"[{고를것}] " if 고를것 else "")
      + f"자리 {len(모두)}곳 · 지시 {지시수}건 · 아직 답 안 한 것 {len(밀림)}건"
      + (f" · 묵은 것 {len(묵은것)}건" if 묵은것 else "") + "\n")

# 옛 방식으로 짝지은 답이 섞여 있으면 그 한계를 적어 준다
옛말 = any(m.get("who") != "나" and "맡은수" not in m for ms in 모두.values() for m in ms)

지금 = time.time()
for at, 자리, 글 in 밀림[-20:]:
    분 = max(0, int((지금 - at) / 60))
    지난 = f"{분}분" if 분 < 90 else f"{분// 60}시간"
    print(time.strftime("%m-%d %H:%M", time.localtime(at)), "|", 자리, "|",
           글[:60].replace("\n", " "), f"| {지난}째")

if 옛말 and (밀림 or 묵은것):
    print("\n(표가 없는 옛 말은 순서로 짝지었다 — 건수는 맞고, 어느 것인지는 어긋날 수 있다.\n"
          " 지금부터 붙는 답은 맡은 지시에 표를 찍으므로 딱 맞는다.)")

if 묵은것:
    print(f"\n묵은 것 {len(묵은것)}건 — 6시간 넘게 답이 없다")
    for at, 자리, 글 in 묵은것[-8:]:
        print(" ", time.strftime("%m-%d %H:%M", time.localtime(at)), "|", 자리, "|",
              글[:56].replace("\n", " "))

if not 고를것:
    print("\n자리별")
    for 자리, ms in sorted(모두.items(), key=lambda x: -max([m.get("at", 0) for m in x[1]] or [0])):
        n = sum(1 for m in ms if m.get("who") == "나")
        밀, 묵 = (lambda t: (len(t[0]), len(t[1])))(밀린것(ms))
        누구, 때 = 답한이(ms)
        꼬리 = f" · 마지막 답 {누구} ({time.strftime('%m-%d %H:%M', time.localtime(때))})" if 누구 else ""
        print(f"  {자리:18s} 지시 {n:3d} · 밀림 {밀}" + (f" · 묵음 {묵}" if 묵 else "") + 꼬리)
    if 밀림:
        print("\n한 자리만 보려면:  python3 tools/지시읽기.py <자리>")
