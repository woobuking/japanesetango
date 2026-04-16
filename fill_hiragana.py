# -*- coding: utf-8 -*-
"""
Jisho API로 N4 히라가나(reading) 자동 채우기
사용법: python fill_hiragana.py
"""
import csv, time, urllib.request, urllib.parse, json, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = 'd:/Projects/japanese tango/DB/'
IN_FILE  = BASE + 'jlpt_words.csv'
OUT_FILE = BASE + 'jlpt_words.csv'

def is_kana(text):
    """이미 히라가나/가타카나로만 이루어진 단어인지 확인"""
    for ch in text:
        name = unicodedata.name(ch, '')
        if ch in ('ー', 'っ', 'ん', 'を'):
            continue
        if 'HIRAGANA' in name or 'KATAKANA' in name:
            continue
        # 한자나 기타 문자 포함 시 False
        return False
    return True

def to_hiragana(katakana):
    """가타카나 → 히라가나 변환"""
    result = []
    for ch in katakana:
        code = ord(ch)
        if 0x30A1 <= code <= 0x30F6:  # ァ ~ ヶ
            result.append(chr(code - 0x60))
        else:
            result.append(ch)
    return ''.join(result)

def jisho_reading(word):
    """일본어 단어 → 히라가나 reading"""
    try:
        url = 'https://jisho.org/api/v1/search/words?keyword=' + urllib.parse.quote(word)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as res:
            data = json.loads(res.read())
        results = data.get('data', [])
        if not results:
            return ''
        # japanese 배열에서 word와 일치하거나 첫 번째 항목의 reading 사용
        for result in results[:3]:
            for jp in result.get('japanese', []):
                word_field = jp.get('word', '')
                reading = jp.get('reading', '')
                if word_field == word and reading:
                    return to_hiragana(reading)
        # 일치 없으면 첫 번째 결과의 첫 번째 reading
        first_jp = results[0].get('japanese', [])
        if first_jp and first_jp[0].get('reading'):
            return to_hiragana(first_jp[0]['reading'])
        return ''
    except Exception as e:
        print(f'  [오류] {word}: {e}')
        return ''

# CSV 읽기
with open(IN_FILE, encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))

fieldnames = list(rows[0].keys())

# 히라가나 빈 N4 단어만
target = [r for r in rows if r['level'] == 'N4' and not r['hiragana'].strip()]
print(f'N4 히라가나 빈 단어: {len(target)}개 처리 시작...\n')

filled = 0
skipped = 0

for i, row in enumerate(target, 1):
    word = row['japanese']

    # 이미 히라가나/가타카나로 이루어진 단어는 그대로 복사
    if is_kana(word):
        row['hiragana'] = word
        filled += 1
        print(f'[{i:3d}/{len(target)}] {word} → (이미 가나) {word}')
        continue

    reading = jisho_reading(word)
    if reading:
        row['hiragana'] = reading
        filled += 1
        print(f'[{i:3d}/{len(target)}] {word} → {reading}')
    else:
        skipped += 1
        print(f'[{i:3d}/{len(target)}] {word} → (찾기 실패)')
    time.sleep(0.3)

# CSV 저장
with open(OUT_FILE, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'\n완료: {filled}개 채움, {skipped}개 실패')
print(f'저장: {OUT_FILE}')
