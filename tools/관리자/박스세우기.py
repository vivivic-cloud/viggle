#!/usr/bin/env python3
"""작업대에 새 박스를 세운다 (`wt_boxes`).

  python3 tools/관리자/박스세우기.py <박스id> "<보일 이름>" [아이콘]

⚠⚠ **박스 id 가 지시 자리 이름이 된다 — `box:<id>` — 그리고 못 바꾼다.** 짧고 읽히게 지어라.
⚠ 칸은 **있는 박스와 똑같이** 채운다(10-15 에 `wt_boxes` 103개를 재서 맞췄다) —
  `name · kind · icon · tone · link · parent · plain · todo · used · created · touched`.
  `link` 는 **빈칸으로 둔다.** 손잡이(`shared/viggle.js`)가 그 칸을 **아예 안 쓴다**
  (프로그램 박스 열다섯 전부 빈칸이고 다 돈다). 10-15 에 그것 때문에 82시간을 헛되이 세웠다.
⚠ `plain: true` 로 두지 마라 — 그 박스에서는 **짚기가 안 걸린다**(10-13 공유판 반품스캔이 그랬다).
⚠ 새 프로그램은 **셋**을 다 갖춰야 한다 — 박스 · 손잡이 · 전담 작업자. 이것은 그 첫째다.
"""
import json, sys, time, urllib.parse, urllib.request
KEY = "AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"; PROJ = "vivivic-4b7ef"
뿌리 = f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"

def 토큰():
    r = urllib.request.urlopen(urllib.request.Request(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
        json.dumps({"returnSecureToken": True}).encode(), {"Content-Type": "application/json"}))
    return json.load(r)["idToken"]

def 세우기(tok, 박스id, 이름, 아이콘):
    이제 = int(time.time())
    칸 = {"name":    {"stringValue": 이름},
          "kind":    {"stringValue": "program"},
          "icon":    {"stringValue": 아이콘},
          "tone":    {"stringValue": "white"},
          "link":    {"stringValue": ""},
          "parent":  {"stringValue": ""},
          "plain":   {"booleanValue": False},
          "todo":    {"booleanValue": False},
          "used":    {"integerValue": "0"},
          "created": {"integerValue": str(이제)},
          "touched": {"integerValue": str(이제)}}
    url = (f"{뿌리}/wt_boxes?documentId={urllib.parse.quote(박스id, safe='')}")
    q = urllib.request.Request(url, json.dumps({"fields": 칸}).encode(),
                               {"Authorization": "Bearer " + tok, "Content-Type": "application/json"},
                               method="POST")
    return json.load(urllib.request.urlopen(q))

if __name__ == "__main__":
    박스id, 이름 = sys.argv[1], sys.argv[2]
    아이콘 = sys.argv[3] if len(sys.argv) > 3 else "package"
    t = 토큰()
    있나 = urllib.request.Request(f"{뿌리}/wt_boxes/{urllib.parse.quote(박스id, safe='')}",
                                  headers={"Authorization": "Bearer " + t})
    try:
        urllib.request.urlopen(있나); print(f"⚠ 이미 있다 — {박스id}. 아무것도 안 했다."); sys.exit(1)
    except urllib.error.HTTPError as e:
        if e.code != 404: raise
    세우기(t, 박스id, 이름, 아이콘)
    print(f"세웠다 · box:{박스id} · 「{이름}」 · 아이콘 {아이콘}")
