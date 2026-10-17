#!/usr/bin/env python3
"""익명 열쇠 한 벌 — 관리자 도구 열넷이 같이 쓴다.

⚠⚠ 왜 있나 — **10-16 에 내가 열쇠를 타다가 막았다.**
   감시를 다시 걸 때마다 `accounts:signUp` 으로 **익명 계정을 새로 하나씩** 만들었다.
   수십 번 만에 `400 TOO_MANY_ATTEMPTS_TRY_LATER` 가 떨어졌고, 그 열쇠를 쓰던
   **관리자 도구 열넷이 한꺼번에** 멈췄다. 16시간 30분을 못 썼고 지시 하나가 843분 묵었다.
→ 한 번 탄 열쇠를 `관리자/본것/열쇠.json` 에 적어 두고 **돌려 쓴다.**
   ㄱ) 아직 안 지났으면 그대로 쓴다 (`signUp` 도 `refresh` 도 안 부른다)
   ㄴ) 지났으면 `securetoken` 으로 **갱신**한다 — 계정을 새로 만들지 않는다
   ㄷ) 갱신까지 안 되면 그때만 `signUp` 한다

쓰는 법 —  `from 열쇠 import 열쇠`  ·  `tok = 열쇠()`
⚠ 적어 둔 파일에 **살아 있는 열쇠**가 들어 있다. 저장소에 올리지 마라(`.gitignore`).
"""
import json, os, time, urllib.parse, urllib.request

KEY = "AIzaSyB9X_hzd2D3goQ7oenK53Pz805P1c7oSqs"
적은곳 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "관리자", "본것", "열쇠.json")
여유 = 300          # 끝나기 5분 전이면 미리 갱신한다


def _보내기(길, 몸, 꼴):
    q = urllib.request.Request(길, 몸, {"Content-Type": 꼴})
    return json.load(urllib.request.urlopen(q, timeout=20))


def _적힌것():
    try:
        with open(적은곳, encoding="utf-8") as f:
            적 = json.load(f)
        if 적.get("idToken") and 적.get("refreshToken"):
            return 적
    except Exception:
        pass
    return None


def _적기(적):
    try:
        os.makedirs(os.path.dirname(적은곳), exist_ok=True)
        with open(적은곳, "w", encoding="utf-8") as f:
            json.dump(적, f)
        os.chmod(적은곳, 0o600)
    except Exception:
        pass            # 못 적어도 열쇠는 돌려준다 — 다음 번에 한 번 더 탈 뿐이다


def _새로():
    r = _보내기(f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={KEY}",
                json.dumps({"returnSecureToken": True}).encode(), "application/json")
    적 = {"idToken": r["idToken"], "refreshToken": r["refreshToken"],
          "끝나는때": time.time() + int(r.get("expiresIn", 3600))}
    _적기(적)
    return 적["idToken"]


def _갱신(적):
    r = _보내기(f"https://securetoken.googleapis.com/v1/token?key={KEY}",
                urllib.parse.urlencode({"grant_type": "refresh_token",
                                        "refresh_token": 적["refreshToken"]}).encode(),
                "application/x-www-form-urlencoded")
    새적 = {"idToken": r["id_token"], "refreshToken": r["refresh_token"],
            "끝나는때": time.time() + int(r.get("expires_in", 3600))}
    _적기(새적)
    return 새적["idToken"]


def 열쇠():
    """살아 있는 idToken 을 돌려준다. 계정은 되도록 새로 만들지 않는다."""
    적 = _적힌것()
    if 적:
        if 적.get("끝나는때", 0) > time.time() + 여유:
            return 적["idToken"]
        try:
            return _갱신(적)
        except Exception:
            pass        # 갱신이 막히면 아래에서 한 번 새로 탄다
    return _새로()

if __name__ == "__main__":
    t = 열쇠()
    적 = _적힌것() or {}
    print("열쇠 %d자 · 남은 초 %d" % (len(t), int(적.get("끝나는때", 0) - time.time())))
