#!/usr/bin/env python3
"""장부(wt_asked)에 상태와 결과를 적는다.

  python3 장부찍기.py <id> <상태> "<결과 한 줄>"

상태는 작업대(viggle/index.html 의 `상태표`)가 아는 여섯뿐이다 —
  받음 · 하는중 · 됐음 · 확인(= 확인 필요, 사장님이 손쓰실 것) · 여쭘 · 못함
⚠ 「확인」 은 **내가 확인했다**가 아니라 **사장님 확인이 필요하다**는 뜻이다. 헷갈리지 마라.
⚠ `결과` 칸을 작업대가 한 줄로 눌러 보여 준다(`처리한줄`). 구구절절 적지 마라.
⚠ 칸 이름이 한글이라 `updateMask.fieldPaths` 에 **백틱**으로 감싸야 한다.
"""
import json, sys, urllib.parse, urllib.request
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from 열쇠 import 열쇠          # 열쇠는 한 벌만 탄다 (10-16 막힌 일)
KEY = "AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"; PROJ = "vivivic-4b7ef"
뿌리 = f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"
상태들 = ("받음", "하는중", "됐음", "확인", "여쭘", "못함")

def 토큰():
    return 열쇠()

def 찍기(tok, 아이디, 상태, 결과):
    assert 상태 in 상태들, f"모르는 상태: {상태} — {상태들}"
    칸 = urllib.parse.quote("wt_asked")
    들 = ["`상태`"] + (["`결과`"] if 결과 else [])
    길 = f"{뿌리}/{칸}/{아이디}?" + "&".join("updateMask.fieldPaths=" + urllib.parse.quote(f) for f in 들)
    몸 = {"fields": {"상태": {"stringValue": 상태}}}
    if 결과: 몸["fields"]["결과"] = {"stringValue": 결과}
    q = urllib.request.Request(길, json.dumps(몸).encode(),
        {"Content-Type": "application/json", "Authorization": "Bearer " + tok}, method="PATCH")
    d = json.load(urllib.request.urlopen(q))
    f = d.get("fields", {})
    print(f"  {아이디} → {f.get('상태',{}).get('stringValue','?')} · {f.get('결과',{}).get('stringValue','')[:60]}")

if __name__ == "__main__":
    아이디, 상태 = sys.argv[1], sys.argv[2]
    결과 = sys.argv[3] if len(sys.argv) > 3 else ""
    찍기(토큰(), 아이디, 상태, 결과)

# ⚠⚠ 10-15 — **아이디를 짐작하지 마라.** 때(초)로 아이디를 지어 찍었다가
#   있지도 않은 줄 `a1792056443` 을 **새로 만들었다**(상태·결과만 든 허깨비).
#   진짜 줄은 `a1792056428` 이었다. Firestore PATCH 는 **없으면 만든다.**
#   → 찍기 전에 `한건본다.py <id>` 로 **그 줄이 진짜 있는지** 보거나,
#     `감시둘` 이 알려 준 아이디·`남은것.py` 가 내놓은 아이디를 **그대로** 써라.
