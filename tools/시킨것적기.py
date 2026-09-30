#!/usr/bin/env python3
"""「내가 시킨 것」 박스에 한 줄을 적는다 / 고친다.

  넣기 : python3 tools/시킨것적기.py 넣기 "box:cabinet-studio" "한 줄" "짚은 자리" "사장님 말씀 그대로" [상태]
  고치기: python3 tools/시킨것적기.py 고치기 <id> 상태=됐음 결과="…" 확인="…" 올린것=abc1234

사장님 말씀(09-30): 「지금 이 채팅창에서 지시한 이내용도 내가 시킨것에 있어야지」.
**짚어서 오신 것만 적으면 반쪽이다.** 채팅으로 주신 것도 같은 자리에 적는다.
상태는 다섯뿐이다 — 하는중 · 됐음 · 확인 · 여쭘 · 못함.
"""
import json, os, sys, time, urllib.request, urllib.parse

KEY  = "AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"
PROJ = "vivivic-4b7ef"
뿌리 = f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"
상태들 = ("하는중", "됐음", "확인", "여쭘", "못함")


def 토큰():
    r = urllib.request.urlopen(urllib.request.Request(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
        json.dumps({"returnSecureToken": True}).encode(), {"Content-Type": "application/json"}))
    return json.load(r)["idToken"]


def 머리():
    return {"Authorization": "Bearer " + 토큰(), "Content-Type": "application/json"}


def 값(v):
    return {"integerValue": str(v)} if isinstance(v, int) else {"stringValue": str(v)}


def 넣기(자리, 한줄, 짚은자리, 말, 상태="하는중"):
    if 상태 not in 상태들:
        sys.exit(f"상태는 {' · '.join(상태들)} 뿐이다 — 받은 것: {상태}")
    때 = int(time.time())
    id = f"a{때}"
    몸 = {"fields": {"자리": 값(자리), "한줄": 값(한줄), "짚은자리": 값(짚은자리),
                    "말": 값(말), "상태": 값(상태), "때": 값(때)}}
    urllib.request.urlopen(urllib.request.Request(
        f"{뿌리}/wt_asked/{id}", json.dumps(몸).encode(), 머리(), method="PATCH"))
    print(f"적었다 · {id} · {상태} · {한줄}")
    return id


def 고치기(id, **바꿀것):
    H = 머리()
    f = json.load(urllib.request.urlopen(urllib.request.Request(f"{뿌리}/wt_asked/{id}", headers=H)))["fields"]
    for k, v in 바꿀것.items():
        if k == "상태" and v not in 상태들:
            sys.exit(f"상태는 {' · '.join(상태들)} 뿐이다 — 받은 것: {v}")
        f[k] = 값(v)
    if "상태" in 바꿀것 and 바꿀것["상태"] in ("됐음", "못함"):
        f["끝난때"] = 값(int(time.time()))
    urllib.request.urlopen(urllib.request.Request(
        f"{뿌리}/wt_asked/{id}", json.dumps({"fields": f}).encode(), H, method="PATCH"))
    print("고쳤다 ·", id, "·", " ".join(f"{k}={v}" for k, v in 바꿀것.items()))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    무엇 = sys.argv[1]
    if 무엇 == "넣기":
        넣기(*sys.argv[2:])
    elif 무엇 == "고치기":
        id = sys.argv[2]
        고치기(id, **dict(a.split("=", 1) for a in sys.argv[3:]))
    else:
        sys.exit(__doc__)
