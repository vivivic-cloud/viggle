#!/bin/bash
# 감시가 살아 있나 — /proc 으로 센다 (ps 는 한글 명령줄을 ? 로 적는다)
N=0
for p in /proc/[0-9]*; do
  [ -r "$p/cmdline" ] || continue
  if tr '\0' ' ' < "$p/cmdline" 2>/dev/null | grep -q "감시둘.py"; then N=$((N+1)); fi
done
S="$(dirname "$0")"
echo "감시둘 $N · 눈금 $(cat "$S/본것/지시.at" 2>/dev/null || echo 없음)"
