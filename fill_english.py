# -*- coding: utf-8 -*-
"""
Jisho API로 영어 필드 빈 단어 자동 채우기
사용법: python fill_english.py
"""
import csv, time, urllib.request, urllib.parse, json, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = 'd:/Projects/japanese tango/DB/'
IN_FILE  = BASE + 'jlpt_words.csv'
OUT_FILE = BASE + 'jlpt_words.csv'

def jisho_lookup(word):
    """일본어 단어 → 영어 뜻 (첫 번째 결과의 첫 번째 뜻)"""
    try:
        url = 'https://jisho.org/api/v1/search/words?keyword=' + urllib.parse.quote(word)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as res:
            data = json.loads(res.read())
        results = data.get('data', [])
        if not results:
            return ''
        # 첫 번째 결과의 영어 뜻들
        senses = results[0].get('senses', [])
        if not senses:
            return ''
        # 첫 번째 sense의 definitions를 '; '로 연결 (최대 3개)
        defs = senses[0].get('english_definitions', [])
        return '; '.join(defs[:3])
    except Exception as e:
        print(f'  [오류] {word}: {e}')
        return ''

# CSV 읽기
with open(IN_FILE, encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))

fieldnames = list(rows[0].keys())

# 빈 영어 단어만 처리
empty_rows = [r for r in rows if not r['english'].strip()]
print(f'영어 빈 단어: {len(empty_rows)}개 처리 시작...\n')

filled = 0
failed = 0

for i, row in enumerate(empty_rows, 1):
    eng = jisho_lookup(row['japanese'])
    if eng:
        row['english'] = eng
        filled += 1
        print(f'[{i:3d}/{len(empty_rows)}] {row["japanese"]} ({row["hiragana"]}) → {eng}')
    else:
        failed += 1
        print(f'[{i:3d}/{len(empty_rows)}] {row["japanese"]} → (찾기 실패)')
    time.sleep(0.3)  # API rate limit 방지

# CSV 저장
with open(OUT_FILE, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'\n완료: {filled}개 채움, {failed}개 실패')
print(f'저장: {OUT_FILE}')
