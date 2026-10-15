#!/usr/bin/env python3
"""장부(wt_asked)에서 **아직 안 끝난 것**을 내놓는다 — 「하는중」 과 「여쭘」.

  python3 tools/관리자/멈춘것.py

⚠⚠ 이것이 없어서 10-15 에 「여쭘」 한 건을 **82시간** 못 봤다.
   `남은것.py` 는 지시판(`wt_dev`)만 본다. 장부(`wt_asked`)는 따로다 —
   작업자가 일은 다 하고도 장부를 「하는중」 으로 두면 사장님 폰에는 **안 끝난 것**으로 보인다.
   10-15 에 그렇게 여덟 건이 서 있었다. **쓸기마다 둘을 다 봐라.**
⚠ 「여쭘」 은 내가 사장님께 여쭤 놓고 세워 둔 것이다. 거기 답이 이미 내 손에 있는 일이 많다
   (10-15 그 건은 「링크를 주십시오」 였는데 링크 칸을 손잡이가 아예 안 쓰는 것이었다).
   여쭈기 전에 **내가 정할 수 있는 것인지** 먼저 봐라.
닫는 것은 `장부찍기.py <id> <상태> "<한 줄>"`.
"""
import json, urllib.request, time
KEY="AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"; PROJ="vivivic-4b7ef"
뿌리=f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"
r=urllib.request.urlopen(urllib.request.Request(
    f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
    json.dumps({"returnSecureToken":True}).encode(),{"Content-Type":"application/json"}))
t=json.load(r)["idToken"]
d=json.load(urllib.request.urlopen(urllib.request.Request(뿌리+"/wt_asked?pageSize=300",headers={"Authorization":"Bearer "+t})))
이제=time.time(); 줄=[]
for doc in d.get("documents",[]):
    f=doc.get("fields",{})
    st=f.get("상태",{}).get("stringValue","")
    if st not in ("하는중","여쭘"): continue
    때=f.get("때",{})
    초=int(때.get("integerValue",0) or 0) or (int(때.get("doubleValue",0) or 0))
    if 초>1e12: 초/=1000
    줄.append((초, st, f.get("자리",{}).get("stringValue",""),
               (f.get("말",{}).get("stringValue","") or f.get("한줄",{}).get("stringValue",""))[:110],
               doc["name"].rsplit("/",1)[1]))
for 초,st,자리,말,i in sorted(줄):
    지남 = int((이제-초)/60) if 초 else "?"
    print(f"[{st}] {지남}분 지남 · {자리} · {i}")
    print(f"     {말}")
