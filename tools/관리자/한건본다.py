#!/usr/bin/env python3
"""장부(wt_asked) 한 건의 **모든 칸**을 그대로 펼쳐 본다.

  python3 tools/관리자/한건본다.py a1791740347

⚠ `한줄` 칸은 **잘려 있다.** 말씀 전문은 `말` 칸이다.
⚠⚠ **`짚은자리` 와 `짚은자`(셀렉터)를 꼭 읽어라 — 거기에 답이 들어 있다.**
   10-15 에 그 둘을 읽고서야 「작업대 · 밴더피아연동」 의 모든박스 격자를 짚으신 것임을 알았다.
"""
import json, urllib.request, sys
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from 열쇠 import 열쇠          # 열쇠는 한 벌만 탄다 (10-16 막힌 일)
KEY="AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"; PROJ="vivivic-4b7ef"
뿌리=f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"
t=열쇠()
d=json.load(urllib.request.urlopen(urllib.request.Request(
    f"{뿌리}/wt_asked/{sys.argv[1]}",headers={"Authorization":"Bearer "+t})))
for k,v in d.get("fields",{}).items():
    s=list(v.values())[0] if v else ""
    print(f"── {k}\n{s}\n")
