#!/usr/bin/env python3
"""지시 하나라도 들어오거나 저장소에 뭐가 올라오면 **그 자리에서 끝난다.**
끝나야 관리자(나)가 깨어난다 — 그래서 돌다 멈추는 꼴로 둔다.
⚠ 상자가 다시 뜨면 /tmp 가 통째로 날아간다(10-10 에 실제로 겪었다).
   그래서 **본 눈금은 파일에** 남기고, 그 파일도 없으면 아래 처음값에서 이어 간다."""
import json, os, subprocess, sys, time, urllib.request

KEY  = "AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"
PROJ = "vivivic-4b7ef"
뿌리  = f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"
여기  = os.path.dirname(os.path.abspath(__file__))
눈금쪽 = os.path.join(여기, "본것", "지시.at")
머리쪽 = os.path.join(여기, "본것", "머리.json")
처음눈금 = 1791594184

def 토큰():
    r = urllib.request.urlopen(urllib.request.Request(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
        json.dumps({"returnSecureToken": True}).encode(),
        {"Content-Type": "application/json"}))
    return json.load(r)["idToken"], time.time()

def 풀기(v):
    k = next(iter(v))
    if k == "arrayValue": return [풀기(x) for x in v[k].get("values", [])]
    if k == "mapValue":   return {a: 풀기(b) for a, b in v[k].get("fields", {}).items()}
    if k == "integerValue": return int(v[k])
    if k == "nullValue":  return None
    return v[k]

def 긁기(tok, 칸):
    req = urllib.request.Request(f"{뿌리}/{칸}?pageSize=300",
                                 headers={"Authorization": "Bearer " + tok})
    d = json.load(urllib.request.urlopen(req))
    밖 = []
    for doc in d.get("documents", []):
        f = {k: 풀기(v) for k, v in doc.get("fields", {}).items()}
        f["_id"] = doc["name"].rsplit("/", 1)[-1]
        밖.append(f)
    return 밖

눈금 = 처음눈금
if os.path.exists(눈금쪽):
    try: 눈금 = int(open(눈금쪽).read().strip())
    except Exception: pass

저장소 = {"apps": "/home/user/vivivic-apps", "cabinet": "/home/user/cabinet-studio", "viggle": "/home/user/viggle"}
머리 = {}
if os.path.exists(머리쪽):
    try: 머리 = json.load(open(머리쪽))
    except Exception: 머리 = {}
for 이름, 길 in 저장소.items():
    if 이름 in 머리 or not os.path.isdir(길): continue
    try: 머리[이름] = subprocess.run(["git","-C",길,"rev-parse","origin/main"],
                                    capture_output=True, text=True).stdout.strip()
    except Exception: pass
json.dump(머리, open(머리쪽, "w"))

tok, 딴때 = 토큰()
print(f"[감시] 켬 — 눈금 {눈금}", flush=True)
while True:
    time.sleep(25)
    try:
        if time.time() - 딴때 > 2400: tok, 딴때 = 토큰()
        새것 = [x for x in 긁기(tok, "wt_asked") if int(x.get("때") or 0) > 눈금]
        if 새것:
            새것.sort(key=lambda x: int(x.get("때") or 0))
            for x in 새것:
                when = time.strftime("%m-%d %H:%M", time.localtime(int(x.get("때") or 0)))
                print(f"새 지시 · {when} · {x.get('자리','')} · [{x.get('짚은자리','')}] "
                      f"{str(x.get('말') or x.get('한줄') or '')}".replace("\n"," ")[:600], flush=True)
            open(눈금쪽, "w").write(str(int(새것[-1].get("때") or 눈금)))
            print("[감시 끝 — 관리자가 받았다. 처리한 뒤 다시 걸어라]", flush=True); sys.exit(0)
    except Exception as e:
        print(f"[감시] 지시 못 읽음 — {e}", flush=True)
    try:
        난것 = []
        for 이름, 길 in 저장소.items():
            if not os.path.isdir(길): continue
            subprocess.run(["git","-C",길,"fetch","-q","origin"], capture_output=True, timeout=120)
            새 = subprocess.run(["git","-C",길,"rev-parse","origin/main"],
                                capture_output=True, text=True).stdout.strip()
            if 새 and 머리.get(이름) and 새 != 머리[이름]:
                글 = subprocess.run(["git","-C",길,"log","-1","--pretty=%h %s",새],
                                    capture_output=True, text=True).stdout.strip()
                난것.append(f"올라왔다 · {이름} · {글}")
            머리[이름] = 새 or 머리.get(이름)
        if 난것:
            json.dump(머리, open(머리쪽, "w"))
            for g in 난것: print(g[:300], flush=True)
            print("[감시 끝 — 관리자가 받았다. 처리한 뒤 다시 걸어라]", flush=True); sys.exit(0)
    except Exception as e:
        print(f"[감시] 저장소 못 봄 — {e}", flush=True)
