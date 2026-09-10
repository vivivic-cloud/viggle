#!/usr/bin/env python3
"""클라우드 작업대에 새 지시가 들어오면 한 줄씩 뱉는다.

맥에 있을 때는 inbox.jsonl 을 tail 로 지켜봤다. 그 자리가 파이어베이스로
옮겨져서, 이제는 여기서 주기적으로 물어본다. 처음 켤 때 이미 있던 것은
내보내지 않고, 그 뒤에 새로 들어온 것만 알린다.
"""
import json, os, sys, time, urllib.request, urllib.parse

KEY  = "AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"
PROJ = "vivivic-4b7ef"
뿌리  = f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents/artifacts/{PROJ}/public/data"
사이  = int(os.environ.get("VG_EVERY", "30"))


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


def 지시들(tok):
    req = urllib.request.Request(f"{뿌리}/wt_dev?pageSize=300",
                                 headers={"Authorization": "Bearer " + tok})
    d = json.load(urllib.request.urlopen(req))
    나온것 = []
    for doc in d.get("documents", []):
        f = {k: 풀기(v) for k, v in doc["fields"].items()}
        자리 = f.get("area", "")
        for i, m in enumerate(f.get("msgs", [])):
            if m.get("who") == "나":
                나온것.append((f"{자리}#{i}", m.get("at", 0), 자리, m.get("text", "")))
    return 나온것


tok, 딴때 = 토큰()
본것 = {k for k, *_ in 지시들(tok)}          # 켤 때 있던 것은 이미 본 것으로 친다
print(f"[감시] 시작 — 이미 있던 지시 {len(본것)}건은 넘어간다", flush=True)

while True:
    time.sleep(사이)
    try:
        if time.time() - 딴때 > 2400:        # 토큰은 한 시간이면 상한다
            tok, 딴때 = 토큰()
        for 표, at, 자리, 글 in 지시들(tok):
            if 표 in 본것:
                continue
            본것.add(표)
            when = time.strftime("%m-%d %H:%M", time.localtime(at))
            print(f"새 지시 · {when} · {자리} · {글}".replace("\n", " ")[:600], flush=True)
    except Exception as e:
        print(f"[감시] 못 읽음 — {e}", flush=True)
