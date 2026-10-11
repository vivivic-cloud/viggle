#!/usr/bin/env python3
"""사장님이 지우라신 박스를 화베에서 지운다.

  python3 박스지우기.py 본뜸.json          # 무엇을 지울지 보여만 준다
  python3 박스지우기.py 본뜸.json 진짜      # 정말 지운다

⚠ **본뜸 파일 없이 돌리지 마라.** 되돌릴 길이 없어진다.
  본뜸은 `적바림/20261010_박스본뜸.json` 처럼 저장소 안에 둔다 — /tmp 는 날아간다.
⚠ 딸린 칸(parent 가 있는 것)을 **먼저** 지운다. 부모를 먼저 지우면 딸린 칸이 떠돈다.
⚠ `vp_*` 는 사장님 uid 라야 손이 닿는다. 나는 못 지운다 — 사장님이 직접 하실 일이다.
"""
import json, sys, urllib.parse, urllib.request
KEY = "AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"; PROJ = "vivivic-4b7ef"
뿌리 = f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"

def 토큰():
    r = urllib.request.urlopen(urllib.request.Request(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
        json.dumps({"returnSecureToken": True}).encode(), {"Content-Type": "application/json"}))
    return json.load(r)["idToken"]

def 지우기(tok, 칸, 아이디):
    q = urllib.request.Request(f"{뿌리}/{urllib.parse.quote(칸)}/{urllib.parse.quote(아이디, safe='')}",
                               headers={"Authorization": "Bearer " + tok}, method="DELETE")
    urllib.request.urlopen(q).read()

def 아이디(x): return x["name"].rsplit("/", 1)[-1]
def 이름(x): return x.get("fields", {}).get("name", {}).get("stringValue", "")

if __name__ == "__main__":
    본 = json.load(open(sys.argv[1], encoding="utf-8"))
    진짜 = len(sys.argv) > 2 and sys.argv[2] == "진짜"
    줄 = ([("wt_boxes", x) for x in 본["딸린칸"]]      # 딸린 칸 먼저
         + [("wt_boxes", x) for x in 본["본체"]]
         + [("wt_dev",   x) for x in 본["지시방"]])
    print(f"{'지운다' if 진짜 else '보기만 한다'} — 모두 {len(줄)}개")
    tok = 토큰() if 진짜 else None
    for 칸, x in 줄:
        i = 아이디(x)
        if 진짜:
            지우기(tok, 칸, i); print(f"  지웠다  {칸}/{i}  {이름(x)}")
        else:
            print(f"  지울 것 {칸}/{i}  {이름(x)}")
    if not 진짜: print("\n정말 지우려면 뒤에 「진짜」 를 붙여라.")
