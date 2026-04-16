# -*- coding: utf-8 -*-
"""
빌드 스크립트: words_data.js를 index.html에 인라인으로 합쳐 단일 HTML 파일 생성
사용법: python build.py
출력: public/index.html (이 파일 하나만 Netlify에 올리면 됨)
"""
import os, shutil

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, 'public')

os.makedirs(OUT, exist_ok=True)

with open(os.path.join(SRC, 'words_data.js'), encoding='utf-8') as f:
    words_js = f.read()

with open(os.path.join(SRC, 'index.html'), encoding='utf-8') as f:
    html = f.read()

# <script src="words_data.js"> 를 인라인 <script>로 교체
bundled = html.replace(
    '<script src="words_data.js"></script>',
    f'<script>{words_js}</script>'
)

out_path = os.path.join(OUT, 'index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(bundled)

size = os.path.getsize(out_path)
print(f'완료: public/index.html ({size // 1024}KB)')
print('→ 이 파일 하나만 Netlify에 올리면 됩니다')
