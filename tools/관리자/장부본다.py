#!/usr/bin/env python3
"""안 끝난 지시와 박스를 센다. (상자가 다시 뜨면 /tmp 가 날아가므로 viggle/tools 로 옮길 것)"""
import json, sys, time, urllib.request
KEY="AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"; PROJ="vivivic-4b7ef"
뿌리=f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"
일꾼={"amt":"에이엠티","cabinet-studio":"NRS","clarify":"제품명료화","boring":"보링변환",
     "layout":"기계배치도","docs":"서류관리","johon":"조혼가구","vendorpia":"벤더피아상품정리",
     "panel":"판재도면기","cartoon":"cartoon"}
def 토큰():
    r=urllib.request.urlopen(urllib.request.Request(
      f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
      json.dumps({"returnSecureToken":True}).encode(),{"Content-Type":"application/json"}))
    return json.load(r)["idToken"]
def 풀기(v):
    k=next(iter(v))
    if k=="arrayValue": return [풀기(x) for x in v[k].get("values",[])]
    if k=="mapValue": return {a:풀기(b) for a,b in v[k].get("fields",{}).items()}
    if k=="integerValue": return int(v[k])
    if k=="nullValue": return None
    return v[k]
def 긁기(tok,칸):
    d=json.load(urllib.request.urlopen(urllib.request.Request(
       f"{뿌리}/{칸}?pageSize=300",headers={"Authorization":"Bearer "+tok})))
    밖=[]
    for doc in d.get("documents",[]):
        f={k:풀기(v) for k,v in doc.get("fields",{}).items()}
        f["_id"]=doc["name"].rsplit("/",1)[-1]; 밖.append(f)
    return 밖
tok=토큰()
지시=긁기(tok,"wt_asked")
남=[x for x in 지시 if x.get("상태") in ("받음","하는중")]   # 됐음·확인은 끝난 것
남.sort(key=lambda x:int(x.get("때") or 0))
지금=time.time()
print(f"⚠ 아직 안 끝난 지시 {len(남)}건 — 오래된 것부터")
for x in 남:
    분=int((지금-int(x.get('때') or 0))/60)
    print(f"  {분:>5}분 · {x.get('자리',''):<22} {x['_id']} · {x.get('상태',''):<5} · {str(x.get('한줄') or '')[:46]}")
박스=긁기(tok,"wt_boxes")
프=[b for b in 박스 if b.get("kind")=="program"]
없=[b["_id"] for b in 프 if b["_id"] not in 일꾼]
print(f"\n프로그램 박스 {len(프)}곳 · 전담 작업자 없는 곳 {len(없)} — 여기 지시는 내가 직접 받는다")
if 없: print("  " + " · ".join(sorted(없)))
