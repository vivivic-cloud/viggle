#!/usr/bin/env python3
"""큐알 규칙표(`큐알규칙`)에 줄을 넣거나 바꾼다.

  python3 큐알규칙넣기.py <줄id> <차례> <이름> <꼴> <갈곳>
  python3 큐알규칙넣기.py --보기

⚠ `갈곳` 은 **http·https** 로 시작해야 한다. `shared/큐알길.js` 가 그 밖은 안 연다.
  {전체} 는 찍힌 글 통째, {1} {2} 는 꼴의 괄호로 잡은 토막이다.
⚠ 이 칸은 `vp_` 가 아니다 — 스캔하는 프로그램이 여럿이라 다 읽을 수 있어야 한다.
"""
import json, sys, urllib.parse, urllib.request
KEY="AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"; PROJ="vivivic-4b7ef"
뿌리=f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"
칸=urllib.parse.quote("큐알규칙")
def 토큰():
    r=urllib.request.urlopen(urllib.request.Request(
      f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
      json.dumps({"returnSecureToken":True}).encode(),{"Content-Type":"application/json"}))
    return json.load(r)["idToken"]
def 풀기(v):
    k=next(iter(v))
    return int(v[k]) if k=="integerValue" else v[k]
tok=토큰()
if len(sys.argv)>1 and sys.argv[1]=="--보기":
    d=json.load(urllib.request.urlopen(urllib.request.Request(
       f"{뿌리}/{칸}?pageSize=300",headers={"Authorization":"Bearer "+tok})))
    for doc in d.get("documents",[]):
        f={k:풀기(v) for k,v in doc.get("fields",{}).items()}
        print("  %-14s 차례%-4s %-14s %s" % (doc["name"].rsplit("/",1)[-1], f.get("차례"), f.get("이름"), f.get("꼴")))
        print("                 → %s" % f.get("갈곳"))
    sys.exit()
줄id, 차례, 이름, 꼴, 갈곳 = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
assert 갈곳.startswith(("http://","https://")), "갈곳은 http 로 시작해야 한다"
몸={"fields":{"이름":{"stringValue":이름},"꼴":{"stringValue":꼴},
     "갈곳":{"stringValue":갈곳},"차례":{"integerValue":str(차례)},"끔":{"booleanValue":False}}}
q=urllib.request.Request(f"{뿌리}/{칸}/{urllib.parse.quote(줄id,safe='')}",
  json.dumps(몸).encode(),{"Content-Type":"application/json","Authorization":"Bearer "+tok},method="PATCH")
json.load(urllib.request.urlopen(q))
print("  넣었다 —", 줄id, "·", 이름)
