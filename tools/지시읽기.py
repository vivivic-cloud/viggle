"""클라우드 작업대에 쌓인 지시를 읽는다. 맥이 없어도 어디서나 된다."""
import json, urllib.request, urllib.parse, sys, time
KEY="AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"; PROJ="vivivic-4b7ef"
뿌리=f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"
def 토큰():
    r=urllib.request.urlopen(urllib.request.Request(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
        json.dumps({"returnSecureToken":True}).encode(),{"Content-Type":"application/json"}))
    return json.load(r)["idToken"]
def 풀기(v):
    k=next(iter(v))
    if k=="stringValue": return v[k]
    if k=="integerValue": return int(v[k])
    if k=="booleanValue": return v[k]
    if k=="doubleValue": return v[k]
    if k=="nullValue": return None
    if k=="arrayValue": return [풀기(x) for x in v[k].get("values",[])]
    if k=="mapValue": return {a:풀기(b) for a,b in v[k].get("fields",{}).items()}
    return v[k]
tok=토큰()
req=urllib.request.Request(f"{뿌리}/wt_dev?pageSize=300",headers={"Authorization":"Bearer "+tok})
d=json.load(urllib.request.urlopen(req))
칸=[]
for doc in d.get("documents",[]):
    f={k:풀기(v) for k,v in doc["fields"].items()}
    for m in f.get("msgs",[]):
        칸.append((m.get("at",0), f.get("area",""), m.get("who",""), m.get("text","")))
칸.sort()
답못한것=[]
자리별={}
for at,area,who,text in 칸: 자리별.setdefault(area,[]).append((at,who,text))
for area,ms in 자리별.items():
    if ms[-1][1]=="나": 답못한것.append((ms[-1][0],area,ms[-1][2]))
답못한것.sort()
print(f"자리 {len(자리별)}곳 · 말 {len(칸)}개 · 아직 답 안 한 것 {len(답못한것)}건\n")
for at,area,text in 답못한것[-10:]:
    print(time.strftime("%m-%d %H:%M",time.localtime(at)),"|",area,"|",text[:70].replace("\n"," "))
