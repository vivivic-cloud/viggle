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


본것쪽 = os.environ.get("VG_SEEN") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".본지시")

tok, 딴때 = 토큰()

# 감시는 이따금 끊긴다. 끊긴 동안 들어온 지시를 다시 켤 때 '이미 본 것' 으로
# 치면 그 지시는 영영 안 나온다 — 조용히 사라진다. 그래서 본 것을 파일에
# 남겨 두고, 다시 켤 때는 그 파일만 믿는다. 파일이 없을 때(맨 처음)만
# 지금 있는 것을 이미 본 것으로 친다.
if os.path.exists(본것쪽):
    with open(본것쪽, encoding="utf-8") as f:
        본것 = {줄.strip() for 줄 in f if 줄.strip()}
    print(f"[감시] 시작 — 본 것 {len(본것)}건은 넘어간다 (끊긴 동안 들어온 것은 이제 알린다)", flush=True)
else:
    본것 = {k for k, *_ in 지시들(tok)}      # 맨 처음 한 번만
    with open(본것쪽, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(본것)))
    print(f"[감시] 처음 켬 — 이미 있던 지시 {len(본것)}건은 넘어간다", flush=True)


def 본것적기():
    with open(본것쪽, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(본것)))

while True:
    time.sleep(사이)
    try:
        if time.time() - 딴때 > 2400:        # 토큰은 한 시간이면 상한다
            tok, 딴때 = 토큰()
        for 표, at, 자리, 글 in 지시들(tok):
            if 표 in 본것:
                continue
            본것.add(표)
            본것적기()                       # 알린 것만 적는다 — 알리기 전에 죽으면 다음에 다시 알린다
            when = time.strftime("%m-%d %H:%M", time.localtime(at))
            print(f"새 지시 · {when} · {자리} · {글}".replace("\n", " ")[:600], flush=True)
    except Exception as e:
        print(f"[감시] 못 읽음 — {e}", flush=True)
