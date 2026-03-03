#!/usr/bin/env python3
import csv
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import requests

REPO = Path('/home/ych/.openclaw/workspace/happyghast')
CSV_PATH = REPO / 'data' / 'happy-ghast_keywords.csv'
USED_PATH = REPO / 'data' / 'used_keywords.json'
NEWS_DIR = REPO / 'src' / 'news'

LOCALES = ["en", "zh-cn", "es", "fr", "de", "ja", "ru", "pt", "ar", "ko"]

I18N = {
    "en": {
        "title": "{kw}: Complete Guide (2026)",
        "desc": "Answering '{kw}' with clear, up-to-date steps and practical Minecraft tips.",
        "h2": "Quick answer",
        "intent": "Search intent: {intent}",
        "guide": "How to handle {kw}",
        "tips": "Practical tips",
        "faq": "FAQ",
    },
    "zh-cn": {
        "title": "{kw}：完整指南（2026）",
        "desc": "围绕“{kw}”提供清晰、实用、可执行的 Minecraft 解答。",
        "h2": "快速结论",
        "intent": "搜索意图：{intent}",
        "guide": "{kw} 的操作步骤",
        "tips": "实用建议",
        "faq": "常见问题",
    },
    "es": {
        "title": "{kw}: Guía completa (2026)",
        "desc": "Respuesta clara y práctica para '{kw}' en Minecraft.",
        "h2": "Respuesta rápida",
        "intent": "Intención de búsqueda: {intent}",
        "guide": "Cómo resolver {kw}",
        "tips": "Consejos prácticos",
        "faq": "Preguntas frecuentes",
    },
    "fr": {
        "title": "{kw} : Guide complet (2026)",
        "desc": "Réponse claire et pratique à '{kw}' dans Minecraft.",
        "h2": "Réponse rapide",
        "intent": "Intention de recherche : {intent}",
        "guide": "Comment gérer {kw}",
        "tips": "Conseils pratiques",
        "faq": "FAQ",
    },
    "de": {
        "title": "{kw}: Kompletter Guide (2026)",
        "desc": "Klare, praktische Antwort auf '{kw}' in Minecraft.",
        "h2": "Kurzantwort",
        "intent": "Suchintention: {intent}",
        "guide": "So löst du {kw}",
        "tips": "Praktische Tipps",
        "faq": "FAQ",
    },
    "ja": {
        "title": "{kw}：完全ガイド（2026）",
        "desc": "Minecraft の「{kw}」をわかりやすく実用的に解説。",
        "h2": "結論",
        "intent": "検索意図：{intent}",
        "guide": "{kw} の進め方",
        "tips": "実用ヒント",
        "faq": "よくある質問",
    },
    "ru": {
        "title": "{kw}: Полный гайд (2026)",
        "desc": "Понятный и практичный ответ по запросу '{kw}' в Minecraft.",
        "h2": "Короткий ответ",
        "intent": "Поисковое намерение: {intent}",
        "guide": "Как решить {kw}",
        "tips": "Практические советы",
        "faq": "FAQ",
    },
    "pt": {
        "title": "{kw}: Guia completo (2026)",
        "desc": "Resposta clara e prática para '{kw}' no Minecraft.",
        "h2": "Resposta rápida",
        "intent": "Intenção de busca: {intent}",
        "guide": "Como fazer {kw}",
        "tips": "Dicas práticas",
        "faq": "FAQ",
    },
    "ar": {
        "title": "{kw}: دليل كامل (2026)",
        "desc": "إجابة واضحة وعملية حول '{kw}' في Minecraft.",
        "h2": "الإجابة السريعة",
        "intent": "نية البحث: {intent}",
        "guide": "كيفية التعامل مع {kw}",
        "tips": "نصائح عملية",
        "faq": "الأسئلة الشائعة",
    },
    "ko": {
        "title": "{kw}: 완전 가이드 (2026)",
        "desc": "Minecraft에서 '{kw}'를 실전 중심으로 쉽게 설명합니다.",
        "h2": "빠른 답변",
        "intent": "검색 의도: {intent}",
        "guide": "{kw} 해결 방법",
        "tips": "실전 팁",
        "faq": "자주 묻는 질문",
    },
}

def run(cmd):
    subprocess.check_call(cmd, cwd=REPO)

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:80] or "happy-ghast-keyword"

def load_used():
    if not USED_PATH.exists():
        return {"used": []}
    return json.loads(USED_PATH.read_text(encoding="utf-8"))

def save_used(data):
    USED_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _to_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default

def pick_keyword():
    used = load_used()
    used_set = {x["keyword"] for x in used.get("used", [])}
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))

    candidates = []
    for row in rows:
        kw = (row.get("Keyword") or "").strip()
        if not kw or kw in used_set:
            continue
        volume = _to_float(row.get("Volume"), 0.0)
        kd = _to_float(row.get("Keyword Difficulty"), 100.0)
        # High volume + low KD priority
        score = volume / (kd + 1.0)
        candidates.append((score, volume, -kd, kw, row))

    if not candidates:
        return None, used

    candidates.sort(reverse=True)
    return candidates[0][4], used

def search_snippets(keyword: str):
    # lightweight search without API key (DuckDuckGo instant answer API)
    url = f"https://api.duckduckgo.com/?q={quote(keyword + ' minecraft')}&format=json&no_redirect=1&no_html=1"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        abstract = (data.get("AbstractText") or "").strip()
        related = data.get("RelatedTopics") or []
        rel_text = []
        for item in related[:5]:
            t = item.get("Text") if isinstance(item, dict) else None
            if t:
                rel_text.append(t)
        return abstract, rel_text
    except Exception:
        return "", []

def build_content(locale, kw, intent, abstract, related):
    t = I18N[locale]
    title = t["title"].format(kw=kw)
    desc = t["desc"].format(kw=kw)
    date = datetime.now(timezone.utc).date().isoformat()
    summary = abstract or f"This page answers the query '{kw}' with practical steps based on current Minecraft mechanics around Happy Ghast."
    bullets = related[:3]
    if not bullets:
        bullets = [
            "Use current release info first (Chase the Skies).",
            "Follow clear steps and avoid outdated preview-only instructions.",
            "Check edition differences (Java vs Bedrock) before acting.",
        ]

    body = f'''---
title: "{title}"
description: "{desc}"
date: {date}
cover: "../happy-ghast-comming-now.png"
---

## {t["h2"]}
{summary}

- {t["intent"].format(intent=intent)}
- Keyword: **{kw}**
- Updated: **{date}**

## {t["guide"].format(kw=kw)}
1. Confirm your game edition (Java or Bedrock).
2. Verify you are on released versions that include Happy Ghast content.
3. Follow the shortest in-game path relevant to this query.
4. Cross-check old preview-era advice before applying it.

## {t["tips"]}
- {bullets[0]}
- {bullets[1]}
- {bullets[2]}

## {t["faq"]}
**Q1: Is this still preview-only?**
No. Happy Ghast content is in released versions from the 2025 game drop cycle.

**Q2: Why do some guides conflict?**
Many old pages were written during preview builds and were never updated.

**Q3: What should I do first in game?**
Start with edition/version check, then execute the shortest path for this keyword.
'''
    return body

def main():
    row, used = pick_keyword()
    if not row:
        print("No unused keywords left.")
        return

    kw = row["Keyword"].strip()
    intent = (row.get("Intent") or "Informational").strip()
    volume = row.get("Volume", "")
    slug = slugify(kw)

    abstract, related = search_snippets(kw)

    for loc in LOCALES:
        target = NEWS_DIR / loc / f"{slug}.mdx"
        target.write_text(build_content(loc, kw, intent, abstract, related), encoding="utf-8")

    run(["git", "pull", "--rebase"])
    run(["git", "add", "src/news", "data/used_keywords.json"])

    used.setdefault("used", []).append({
        "keyword": kw,
        "slug": slug,
        "intent": intent,
        "volume": volume,
        "used_at_utc": datetime.now(timezone.utc).isoformat()
    })
    save_used(used)

    run(["git", "add", "src/news", "data/used_keywords.json"])
    run(["git", "commit", "-m", f"Daily keyword post: {kw}"])
    run(["git", "push"])
    print(f"Done: {kw}")

if __name__ == "__main__":
    main()
