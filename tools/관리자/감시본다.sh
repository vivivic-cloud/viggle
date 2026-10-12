#!/bin/bash
# 감시가 살아 있나 — /proc 으로 센다 (ps 는 한글 명령줄을 ? 로 적는다)
#
# ⚠ 10-12 에 이 자가 두 번 틀렸다. 「감시둘.py」 가 들어 있기만 하면 세었더니
#   ㄱ) 감시를 감싸고 있는 bash -c 껍데기까지 세어 1개를 2개로 적었고
#   ㄴ) 이 자를 부르는 내 명령줄 자체가 걸려 또 늘었다.
#   그래서 겹친 줄 알고 멀쩡한 감시를 죽이려 들었다.
#   → 이제 명령줄이 **python3 감시둘.py 딱 그것**일 때만 센다.
N=0; PIDS=""
for p in /proc/[0-9]*; do
  [ -r "$p/cmdline" ] || continue
  C="$(tr '\0' '|' < "$p/cmdline" 2>/dev/null)"
  if [ "$C" = "python3|감시둘.py|" ]; then N=$((N+1)); PIDS="$PIDS ${p##*/}"; fi
done
S="$(dirname "$0")"
echo "감시둘 $N$PIDS · 눈금 $(cat "$S/본것/지시.at" 2>/dev/null || echo 없음)"
