# -*- coding: utf-8 -*-
import pdfplumber, openpyxl, pandas as pd, csv, warnings
warnings.filterwarnings('ignore')

base = 'd:/Projects/japanese tango/DB/'
rows = []

# ── N5 xlsx ──────────────────────────────────────
wb = openpyxl.load_workbook(base + '일본어JLPT레벨N5단어장.xlsx')
ws = wb.active
data = list(ws.iter_rows(values_only=True))
for i, r in enumerate(data[1:], 1):
    japanese = str(r[1] or '').strip()
    if not japanese or japanese == 'None':
        continue
    rows.append({
        'word_id': f'N5-{i:04d}',
        'level': 'N5',
        'japanese': japanese,
        'hiragana': str(r[5] or '').strip(),
        'korean':   str(r[2] or '').strip(),
        'english':  str(r[3] or '').strip(),
        'category': '',
        'emoji':    ''
    })
print(f'N5: {sum(1 for r in rows if r["level"]=="N5")}개')

# ── N4 xlsx ──────────────────────────────────────
df4 = pd.read_excel(base + '일본어JLPT레벨N4단어장.xlsx', engine='openpyxl')
n4_start = len(rows)
for i, r in df4.iterrows():
    japanese = str(r.iloc[1]).strip()
    if not japanese or japanese == 'nan':
        continue
    rows.append({
        'word_id': f'N4-{i+1:04d}',
        'level': 'N4',
        'japanese': japanese,
        'hiragana': '',
        'korean':   str(r.iloc[2]).strip() if str(r.iloc[2]) != 'nan' else '',
        'english':  str(r.iloc[3]).strip() if str(r.iloc[3]) != 'nan' else '',
        'category': '',
        'emoji':    ''
    })
print(f'N4: {len(rows) - n4_start}개')

# ── N3 PDF 파서 ───────────────────────────────────
def parse_pdf(path, category):
    words = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in (page.extract_tables() or []):
                for row in table[1:]:
                    if not row or not row[0]:
                        continue
                    try:
                        int(str(row[0]).strip())
                    except ValueError:
                        continue
                    japanese = str(row[1] or '').strip()
                    hiragana = str(row[2] or '').strip()
                    korean   = str(row[-1] or '').strip()
                    if japanese:
                        words.append((japanese, hiragana, korean))
    return words

n3_files = [
    ('JLPT N3 필수 동사 정리.pdf',            '동사'),
    ('JLPT N3 필수 명사 정리.pdf',            '명사'),
    ('JLPT N3 핵심 명사 정리 (い형용사).pdf',  'い형용사'),
    ('JLPT N3 핵심 명사 정리 (な형용사).pdf',  'な형용사'),
]
n3_start = len(rows)
for fname, cat in n3_files:
    words = parse_pdf(base + fname, cat)
    prefix = {'동사': 'V', '명사': 'N', 'い형용사': 'I', 'な형용사': 'A'}[cat]
    for j, (japanese, hiragana, korean) in enumerate(words, 1):
        rows.append({
            'word_id': f'N3-{prefix}-{j:04d}',
            'level': 'N3',
            'japanese': japanese,
            'hiragana': hiragana,
            'korean':   korean,
            'english':  '',
            'category': cat,
            'emoji':    ''
        })
    print(f'  N3 {cat}: {len(words)}개')
print(f'N3 합계: {len(rows) - n3_start}개')

# ── CSV 저장 ──────────────────────────────────────
out = base + 'jlpt_words.csv'
with open(out, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(
        f,
        fieldnames=['word_id','level','japanese','hiragana','korean','english','category','emoji']
    )
    writer.writeheader()
    writer.writerows(rows)

print(f'\n총 {len(rows)}개 단어 → {out}')
