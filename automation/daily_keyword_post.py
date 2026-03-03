#!/usr/bin/env python3
import argparse
import csv
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import requests

REPO = Path('/home/ych/.openclaw/workspace/happyghast')
CSV_PATH = REPO / 'data' / 'happy-ghast_keywords.csv'
USED_PATH = REPO / 'data' / 'used_keywords.json'
USED_IMAGES_PATH = REPO / 'data' / 'used_images.json'
NEWS_DIR = REPO / 'src' / 'news'

LOCALES = ["en", "zh-cn", "es", "fr", "de", "ja", "ru", "pt", "ar", "ko"]

I18N = {
    "en": {"title": "{kw}: Complete Guide (2026)", "desc": "A detailed, intent-matched guide for '{kw}' with practical, up-to-date Minecraft steps."},
    "zh-cn": {"title": "{kw}：完整指南（2026）", "desc": "围绕“{kw}”的深度攻略，覆盖搜索意图、实操步骤与常见误区。"},
    "es": {"title": "{kw}: Guía completa (2026)", "desc": "Guía extensa y práctica para '{kw}' en Minecraft."},
    "fr": {"title": "{kw} : Guide complet (2026)", "desc": "Guide détaillé et pratique pour '{kw}' dans Minecraft."},
    "de": {"title": "{kw}: Kompletter Guide (2026)", "desc": "Ausführlicher, praxisnaher Guide zu '{kw}' in Minecraft."},
    "ja": {"title": "{kw}：完全ガイド（2026）", "desc": "「{kw}」を検索意図に沿って詳しく解説する実践ガイド。"},
    "ru": {"title": "{kw}: Полный гайд (2026)", "desc": "Подробный практический гайд по запросу '{kw}' в Minecraft."},
    "pt": {"title": "{kw}: Guia completo (2026)", "desc": "Guia detalhado e prático para '{kw}' no Minecraft."},
    "ar": {"title": "{kw}: دليل كامل (2026)", "desc": "دليل تفصيلي وعملي حول '{kw}' في Minecraft."},
    "ko": {"title": "{kw}: 완전 가이드 (2026)", "desc": "'{kw}'를 검색 의도 중심으로 깊이 있게 정리한 실전 가이드."},
}

def run(cmd):
    subprocess.check_call(cmd, cwd=REPO)

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")[:80] or "happy-ghast-keyword"

def read_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def to_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default

def pick_keyword(force_keyword=None):
    used = read_json(USED_PATH, {"used": []})
    if force_keyword:
        rows = list(csv.DictReader(CSV_PATH.open(encoding='utf-8')))
        for row in rows:
            if (row.get('Keyword') or '').strip().lower() == force_keyword.strip().lower():
                return row, used
        return None, used

    used_set = {x['keyword'] for x in used.get('used', [])}
    rows = list(csv.DictReader(CSV_PATH.open(encoding='utf-8')))
    candidates = []
    for row in rows:
        kw = (row.get('Keyword') or '').strip()
        if not kw or kw in used_set:
            continue
        vol = to_float(row.get('Volume'), 0.0)
        kd = to_float(row.get('Keyword Difficulty'), 100.0)
        score = vol / (kd + 1.0)  # high volume + low KD
        candidates.append((score, vol, -kd, kw, row))
    if not candidates:
        return None, used
    candidates.sort(reverse=True)
    return candidates[0][4], used

def download_unique_cover(slug):
    used_images = read_json(USED_IMAGES_PATH, {"used": []})
    used_set = set(used_images.get('used', []))
    ts = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    seed = f"{slug}-{ts}"
    url = f"https://picsum.photos/seed/{seed}/1600/900"
    r = requests.get(url, timeout=30, allow_redirects=True)
    r.raise_for_status()
    final_url = r.url
    if final_url in used_set:
        seed = f"{seed}-a"
        r = requests.get(f"https://picsum.photos/seed/{seed}/1600/900", timeout=30, allow_redirects=True)
        r.raise_for_status()
        final_url = r.url
    cover_name = f"{slug}-{datetime.now(timezone.utc).strftime('%Y%m%d')}.jpg"
    cover_path = REPO / 'src' / 'news' / cover_name
    cover_path.write_bytes(r.content)
    used_images.setdefault('used', []).append(final_url)
    write_json(USED_IMAGES_PATH, used_images)
    return cover_name, final_url

def long_body(kw, intent, volume, kd, cpc, locale, image_source):
    date = datetime.now(timezone.utc).date().isoformat()
    heading = {
        'zh-cn': '核心结论', 'ja': '結論', 'ko': '핵심 요약', 'ar': 'الخلاصة',
        'en': 'Core answer'
    }.get(locale, 'Core answer')

    # ~1200+ English words (with minor locale wrapper labels)
    return f'''## {heading}
If you searched for **{kw}**, your goal is usually simple: get a clear, current, no-fluff path that works in released Minecraft builds. This guide is intentionally long-form so you can finish with both understanding and execution confidence.

- Keyword: **{kw}**
- Intent: **{intent}**
- Market signals: Volume **{volume}**, KD **{kd}**, CPC **{cpc}**
- Updated: **{date}**

## What this keyword usually means in practice
Players typing **{kw}** are often in one of four states:
1. They heard about Happy Ghast but are unsure what is already released.
2. They found old preview content and now have conflicting instructions.
3. They want the shortest playable route, not lore-heavy explanation.
4. They need to avoid wasting resources in survival mode.

That means the best article must do three things well: confirm version reality, provide an action sequence, and highlight mistakes that create confusion.

## Version-first thinking (why most guides fail)
Most frustration comes from timeline mismatch. A lot of pages were published during preview snapshots and never updated. So before any crafting/farming/taming steps, you should always check:

- Are you on a released build that includes Happy Ghast mechanics?
- Are you following Java or Bedrock specific instructions?
- Is your source referencing old preview-only behavior?

This one habit prevents most dead ends. In other words, version mismatch—not gameplay complexity—is the biggest reason players think a guide is "wrong."

## Practical route that works for most players
Use this sequence whenever you target **{kw}**:

### Step 1: Confirm edition and world context
Open your game info first. Note edition, version, and whether your world has any custom datapacks/addons that alter mob behavior.

### Step 2: Define your objective in one sentence
For example: "I need a reliable Happy Ghast setup for survival travel." This prevents collecting items you don't need.

### Step 3: Gather minimum viable resources
Do not overfarm. Start with only what the shortest route needs, then expand after first success.

### Step 4: Execute in controlled order
Run one change at a time and verify result. If you change three things at once, debugging becomes guesswork.

### Step 5: Lock in repeatability
When you succeed once, document exact coordinates, resource count, and timing so you can reproduce the workflow.

## Common mistakes and how to avoid them
### Mistake A: Treating old preview advice as current truth
Fix: prioritize current release documentation and updated community notes.

### Mistake B: Mixing Java and Bedrock assumptions
Fix: if a mechanic feels inconsistent, check edition difference before assuming bug.

### Mistake C: Optimizing too early
Fix: first achieve one successful loop. Then optimize speed, cost, or aesthetics.

### Mistake D: Building without rollback safety
Fix: in survival, keep backups and avoid high-risk edits before validation.

## SEO intent alignment: informational + transactional
This keyword often has mixed intent. Users want both understanding and immediate action. So your page should include:

- A direct answer section (for fast readers)
- A verified action flow (for players doing it now)
- A troubleshooting matrix (for players blocked mid-process)
- A short FAQ with clear yes/no answers

That structure keeps bounce low and helps users self-qualify without jumping across multiple pages.

## Troubleshooting matrix
### Problem: "I followed a guide but result is different"
Likely cause: edition/version mismatch.
Action: re-check source date and game edition assumptions.

### Problem: "Resource usage feels too high"
Likely cause: over-collection before proof-of-work.
Action: restart with minimum viable resources and scale after first success.

### Problem: "Behavior changed after update"
Likely cause: patch-level mechanic adjustment.
Action: re-validate one step at a time and compare release notes.

### Problem: "Works in one world, fails in another"
Likely cause: world modifiers (addons, datapacks, server configs).
Action: test in clean world to isolate baseline behavior.

## Efficient content operations for this keyword cluster
If you are publishing around Happy Ghast long-tail terms, keep an internal template:

1. One core definitive guide (this page type)
2. One short answer page for each long-tail query
3. One cross-link block connecting release date, crafting path, ride/tether behavior, and edition differences
4. One update log section so users trust freshness

This method helps ranking stability and also reduces maintenance cost when mechanics shift.

## Why this long format matters
Short pages can rank briefly, but they often fail intent completion. For mixed-intent game keywords, users need a page that answers both "what is true now" and "what do I do next." Long format lets you:

- answer beginner confusion,
- support mid-level execution,
- and reduce support comments caused by outdated snippets.

In practical terms, a complete page saves user time and increases trust, which is exactly what search engines reward over time.

## FAQ
**Q1: Is this keyword still relevant after release?**
Yes. After release, search intent shifts from speculation to execution and troubleshooting.

**Q2: Should I prioritize fast answers or long explanations?**
Both: put fast answers first, then provide depth for users who continue reading.

**Q3: What is the best first action when uncertain?**
Check edition + version first. It solves most confusion before any in-game action.

**Q4: Why include market metrics in planning?**
Volume/KD/CPC help prioritize what to publish next and where to spend writing depth.

## Image source
- {image_source}
'''

def build_post(locale, kw, intent, volume, kd, cpc, cover_name, image_source):
    t = I18N[locale]
    title = t['title'].format(kw=kw)
    desc = t['desc'].format(kw=kw)
    date = datetime.now(timezone.utc).date().isoformat()
    body = long_body(kw, intent, volume, kd, cpc, locale, image_source)
    return f'''---
title: "{title}"
description: "{desc}"
date: {date}
cover: "../{cover_name}"
---

{body}
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keyword', help='Force a specific keyword (case-insensitive)')
    parser.add_argument('--no-mark-used', action='store_true', help='Do not mark keyword as used')
    args = parser.parse_args()

    row, used = pick_keyword(args.keyword)
    if not row:
        print('No keyword selected.')
        return

    kw = (row.get('Keyword') or '').strip()
    intent = (row.get('Intent') or 'Informational').strip()
    volume = row.get('Volume', '')
    kd = row.get('Keyword Difficulty', '')
    cpc = row.get('CPC (USD)', '')
    slug = slugify(kw)

    cover_name, image_source = download_unique_cover(slug)

    for loc in LOCALES:
        target = NEWS_DIR / loc / f'{slug}.mdx'
        target.write_text(build_post(loc, kw, intent, volume, kd, cpc, cover_name, image_source), encoding='utf-8')

    if not args.no_mark_used:
        used.setdefault('used', []).append({
            'keyword': kw,
            'slug': slug,
            'intent': intent,
            'volume': volume,
            'kd': kd,
            'used_at_utc': datetime.now(timezone.utc).isoformat()
        })
        write_json(USED_PATH, used)

    run(['git', 'pull', '--rebase'])
    run(['git', 'add', 'src/news', 'data/used_keywords.json', 'data/used_images.json', 'automation/daily_keyword_post.py'])
    run(['npm', 'run', 'build'])
    run(['git', 'commit', '-m', f'Daily keyword post: {kw}'])
    run(['git', 'push'])
    print(f'Done: {kw}')

if __name__ == '__main__':
    main()
