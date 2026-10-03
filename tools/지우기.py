#!/usr/bin/env python3
"""작업대에 쌓인 지시와 답을 지운다. **정말로 지운다 — 되돌릴 수 없다.**

  python3 tools/지우기.py                      무엇이 있는지 보기만 한다 (아무것도 안 지움)
  python3 tools/지우기.py --자리 box:amt        그 자리만 본다
  python3 tools/지우기.py --남길 20             최근 20개만 남기고 나머지를 지운다 (보기만)
  python3 tools/지우기.py --남길 20 --진짜      ← 진짜로 지운다
  python3 tools/지우기.py --전부 --진짜         ← 모두 지운다 (자리는 남고 글만 비운다)
  python3 tools/지우기.py --시킨것 --진짜       「내가 시킨 것」 기록도 같이 지운다

**`--진짜` 를 붙이기 전에는 한 글자도 안 지운다.**
"""
import json, sys, urllib.request, urllib.parse

KEY  = "AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"
PROJ = "vivivic-4b7ef"
뿌리  = f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents"
데이터 = f"{뿌리}/artifacts/{PROJ}/public/data"


def 토큰():
    r = urllib.request.urlopen(urllib.request.Request(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
        json.dumps({"returnSecureToken": True}).encode(), {"Content-Type": "application/json"}))
    return json.load(r)["idToken"]


def 부르기(길, tok, 어떻게="GET", 몸=None):
    q = urllib.request.Request(길, method=어떻게,
        data=json.dumps(몸).encode() if 몸 is not None else None,
        headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    with urllib.request.urlopen(q) as r:
        t = r.read()
        return json.loads(t) if t else {}


def 크기(x):
    return len(json.dumps(x, ensure_ascii=False).encode())


자리고름 = None; 남길 = None; 전부 = False; 진짜 = False; 시킨것도 = False
i = 1
while i < len(sys.argv):
    a = sys.argv[i]
    if a == "--자리":   자리고름 = sys.argv[i+1]; i += 1
    elif a == "--남길": 남길 = int(sys.argv[i+1]); i += 1
    elif a == "--전부": 전부 = True
    elif a == "--진짜": 진짜 = True
    elif a == "--시킨것": 시킨것도 = True
    i += 1

tok = 토큰()
d = 부르기(f"{데이터}/wt_dev?pageSize=300", tok)
문서들 = d.get("documents", [])

할일 = []
for doc in 문서들:
    f = doc.get("fields", {})
    자리 = f.get("area", {}).get("stringValue", "?")
    if 자리고름 and 자리 != 자리고름: continue
    글들 = f.get("msgs", {}).get("arrayValue", {}).get("values", [])
    before = 크기(doc)
    if 전부:        남는것 = []
    elif 남길 is not None: 남는것 = 글들[-남길:] if 남길 > 0 else []
    else:           남는것 = 글들            # 보기만
    할일.append((doc, 자리, len(글들), len(남는것), before))

print(f"\n{'자리':<24}{'지금':>6}{'남길':>6}{'지울것':>7}{'크기':>10}")
print("-" * 55)
지울글 = 0; 지울바이트 = 0
for doc, 자리, 있음, 남음, before in sorted(할일, key=lambda x: -x[4]):
    지움 = 있음 - 남음
    지울글 += 지움
    if 있음: 지울바이트 += before * 지움 // 있음
    print(f"{자리:<24}{있음:>6}{남음:>6}{지움:>7}{before/1024:>8.0f}KB")
print("-" * 55)
print(f"지울 글 {지울글}개 · 줄어들 크기 약 {지울바이트/1024:.0f}KB")

시킨것들 = []
if 시킨것도:
    a = 부르기(f"{데이터}/wt_asked?pageSize=300", tok)
    시킨것들 = a.get("documents", [])
    print(f"「내가 시킨 것」 기록 {len(시킨것들)}개도 지운다")

if not 진짜:
    print("\n** 보기만 했다. 아무것도 안 지웠다. **")
    print("   정말 지우려면 뒤에 --진짜 를 붙여라.\n")
    sys.exit(0)

if 지울글 == 0 and not 시킨것들:
    print("\n지울 것이 없다.\n"); sys.exit(0)

print("\n>> 진짜로 지운다 ...")
for doc, 자리, 있음, 남음, _ in 할일:
    if 있음 == 남음: continue
    글들 = doc["fields"]["msgs"]["arrayValue"]["values"]
    남는것 = 글들[-남음:] if 남음 > 0 else []
    길 = doc["name"].replace("projects/", f"{'https://firestore.googleapis.com/v1/projects/'}", 1) \
         if doc["name"].startswith("projects/") else doc["name"]
    길 = "https://firestore.googleapis.com/v1/" + doc["name"] + "?updateMask.fieldPaths=msgs"
    부르기(길, tok, "PATCH", {"fields": {"msgs": {"arrayValue": {"values": 남는것}}}})
    print(f"   {자리}: {있음} → {남음}")

for doc in 시킨것들:
    부르기("https://firestore.googleapis.com/v1/" + doc["name"], tok, "DELETE")
if 시킨것들:
    print(f"   「내가 시킨 것」 {len(시킨것들)}개 지웠다")

print(">> 끝났다. 되돌릴 수 없다.\n")
