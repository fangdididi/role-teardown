#!/usr/bin/env python3
"""role-teardown helper: read a job posting the way a parser and a skimmer do.

Subcommands
  signals  POSTING            ranked requirement terms, hard gates, section mix
  coverage POSTING CV         which weighted terms your CV carries, and where
  lint     DRAFT [--max N]    generic phrases, duty-style bullets, missing numbers

Plain text or Markdown in, plain report out (add --json for machine output).
Works with English and Chinese text. Standard library only.
"""
import argparse
import json
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------- sections
SECTION_RULES = [
    # (kind, weight, header patterns)
    ("must", 3.0, r"requirement|qualification|must[- ]have|what you (?:bring|need)|you have|who you are|"
                  r"任职要求|任职资格|岗位要求|职位要求|我们希望你|硬性要求"),
    ("nice", 1.0, r"nice[- ]to[- ]have|bonus|preferred|plus\b|good to have|extra credit|加分|优先考虑|锦上添花"),
    ("duty", 2.0, r"responsibilit|what you(?:'|’)?ll do|you will|the role|day[- ]to[- ]day|your impact|"
                  r"岗位职责|工作内容|职责描述|你将负责|工作职责"),
    ("noise", 0.0, r"about (?:us|the company)|benefit|perks|we offer|equal opportunit|compensation|salary|"
                   r"why join|关于我们|公司介绍|福利|薪资|我们提供|公司简介"),
]
DEFAULT_WEIGHT = 1.5
HEDGE = re.compile(r"\b(?:preferred|nice to have|bonus|a plus|ideally|familiarity with|exposure to)\b|优先|加分|者佳|了解即可",
                   re.I)
HEADER_HINT = re.compile(r"^\s*(?:#{1,6}\s+|\*\*.+\*\*\s*:?\s*$|[A-Za-z\u4e00-\u9fff][^.。]{0,40}[:：]\s*$)")

GATE_RULES = [
    ("experience", r"\d+\s*\+?\s*(?:-\s*\d+\s*)?(?:years?|yrs)\b|\d+\s*年以上|\d+\s*-\s*\d+\s*年|\d+年(?:及以上|经验)"),
    ("degree", r"bachelor|master'?s|\bph\.?d\b|\bdegree\b|\bBS\b|\bMS\b|本科|硕士|博士|学历|统招"),
    ("location", r"on-?site|in office|relocat|hybrid|\bremote\b|time ?zone|驻场|坐班|出差|远程|base\s*\S+|工作地点"),
    ("authorization", r"visa|sponsor|work authori[sz]ation|right to work|citizenship|clearance|签证|户口"),
    ("language", r"fluent|native speaker|proficien\w* in (?:english|german|french|japanese|chinese|spanish)|"
                 r"英语|英文|日语|CET-?[46]|雅思|托福"),
]

FUNCTION = set("""a an the and or of to in for on with by at as is are be will you your our we us this that it its from
into across within about over per via who what which their they them can may must should would could has have
having been being not no all any each other more most such than then so do does did make makes help team teams
work working role new strong good great ability able experience experienced years year plus etc using use including
also well both one two three four five who's you'll we're it's like across up out own ideally highly""".split())
GENERIC = set("""data day days week weeks time today people customers customer company code review reviews things way part full""".split())
STOP = FUNCTION | GENERIC

CJK = re.compile(r"[\u4e00-\u9fff]")
CJK_TRIM_PREFIX = re.compile(r"^(?:熟练使用|熟练|熟悉|精通|掌握|了解|具备|拥有|具有|能够|独立|看懂|写出|负责|参与|搭建|维护|设计|分析|输出|"
                             r"收集|撰写|定义|持续|一起|按照|按|基于|通过|使用|良好|较强|优秀|扎实|丰富|一定|相关|深度|"
                             r"能|会|懂|有|用|做|如|含|将|让|自己|以上|及以上)+")
CJK_TRIM_SUFFIX = re.compile(r"(?:经验|能力|者优先|优先|者佳|加分|流畅|工作|方面|等|上|中)+$")
CJK_FUNCTION_SPLIT = re.compile(r"[的和与及或并等在对把从到为是了]")
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9+#./-]*[A-Za-z0-9+#]|[A-Za-z]")
BULLET_PREFIX = re.compile(r"^\s*(?:[-*\u2022\u00b7]|\d+[.)\u3001])\s+")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?\u3002\uff01\uff1f\uff1b;])\s+|(?<=[\u3002\uff01\uff1f\uff1b])")
SPLIT_CJK = re.compile(r"[，。、；：,;:（）()\[\]【】《》“”\"'!?！？/\s|·•]+")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def classify_header(line):
    text = line.strip().strip("#*").strip()
    if not text or len(text) > 60:
        return None
    if not HEADER_HINT.match(line) and len(text.split()) > 6:
        return None
    for kind, weight, pat in SECTION_RULES:
        if re.search(pat, text, re.I):
            return kind, weight
    return None


def norm(term):
    return re.sub(r"[\s.\-_/]", "", term.lower())


def line_terms(line):
    """Candidate terms in one line: tech-looking tokens, short Latin phrases, CJK chunks."""
    out = []
    line = BULLET_PREFIX.sub("", line).replace("**", "")
    for m in LATIN_TOKEN.finditer(line):
        bare = m.group(0).strip(".-/")
        low = bare.lower()
        if low in STOP or len(bare) < 2 and bare not in ("C", "R"):
            continue
        before = line[: m.start()].rstrip()
        sentence_start = not before or before[-1] in ".:!?;。："
        shaped = any(ch.isupper() for ch in bare[1:]) or any(ch in "+#./" for ch in bare) \
            or any(ch.isdigit() for ch in bare) or (bare.isupper() and len(bare) >= 2)
        techy = shaped or (bare[0].isupper() and not sentence_start)
        out.append((bare, techy))
    # two- and three-word Latin phrases made of non-stopwords
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9+#-]*", line)]
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            chunk = words[i:i + n]
            if any(w.lower() in FUNCTION for w in chunk) or all(w.lower() in GENERIC for w in chunk):
                continue
            out.append((" ".join(chunk), False))
    # CJK chunks
    if CJK.search(line):
        for piece in SPLIT_CJK.split(line):
            piece = re.sub(r"[A-Za-z0-9+#.\-]+", " ", piece).strip()
            for sub in CJK_FUNCTION_SPLIT.sub(" ", piece).split():
                sub = CJK_TRIM_SUFFIX.sub("", CJK_TRIM_PREFIX.sub("", sub))
                if 2 <= len(sub) <= 8 and CJK.search(sub) and not re.fullmatch(r"[\d一二三四五六七八九十百千万]+[年个周天月次]?", sub):
                    out.append((sub, len(sub) <= 5))
    return out


def analyse(text):
    lines = text.splitlines()
    has_sections = any(classify_header(l) for l in lines if l.strip())
    # lines before the first recognised section are usually title and meta (company, city, contract type)
    kind, weight = ("preamble", 0.0) if has_sections else ("unlabelled", DEFAULT_WEIGHT)
    pos_in_section = 0
    scores = defaultdict(float)
    counts = defaultdict(int)
    kinds = defaultdict(set)
    display = {}
    techy_seen = defaultdict(bool)
    section_lines = defaultdict(int)
    gates = []
    title = None
    for raw in lines:
        if not raw.strip():
            continue
        head = classify_header(raw)
        if head:
            kind, weight = head
            pos_in_section = 0
            continue
        if re.match(r"^\s*#{1,6}\s", raw):  # an unrecognised heading: remember the first as the title
            title = title or raw.strip().lstrip("#").strip()
            continue
        pos_in_section += 1
        section_lines[kind] += 1
        early = 1.0 + max(0, 4 - pos_in_section) * 0.1  # first lines of a block weigh a little more
        # a one-paragraph posting mixes must-haves and nice-to-haves, so judge sentence by sentence
        seen_here = set()  # count a term once per line
        for sent in SENTENCE_SPLIT.split(raw):
            if not sent.strip():
                continue
            hedged = bool(HEDGE.search(sent))
            w = min(weight, 1.0) if (kind != "noise" and hedged) else weight
            for gname, pat in GATE_RULES:
                if re.search(pat, sent, re.I):
                    gates.append({"type": gname, "line": BULLET_PREFIX.sub("", sent).replace("**", "").strip(),
                                  "soft": hedged, "in_benefits": kind == "noise"})
            for term, techy in line_terms(sent):
                key = norm(term)
                if not key or key in seen_here:
                    continue
                seen_here.add(key)
                scores[key] += w * early
                counts[key] += 1
                kinds[key].add(kind)
                techy_seen[key] |= techy
                display.setdefault(key, term)
    ranked = []
    for key, s in scores.items():
        if s <= 0.01:
            continue
        multiword = " " in display[key]
        # keep a term if it looks like a named skill, or the posting repeats it
        if not (techy_seen[key] or counts[key] >= 2 or (multiword and counts[key] >= 2)):
            continue
        if multiword and counts[key] < 2:
            continue
        ranked.append({"term": display[key], "score": round(s, 2), "count": counts[key],
                       "sections": sorted(kinds[key])})
    # drop single words that only ever appear inside a kept phrase with the same count
    phrases = [r for r in ranked if " " in r["term"]]
    kept = []
    for r in ranked:
        if " " not in r["term"] and any(r["term"].lower() in p["term"].lower().split() and p["count"] >= r["count"]
                                         for p in phrases):
            continue
        kept.append(r)
    kept.sort(key=lambda r: (-r["score"], -r["count"], r["term"].lower()))
    total = sum(section_lines.values()) or 1
    mix = {k: round(v / total, 2) for k, v in sorted(section_lines.items())}
    return {"title": title, "terms": kept, "gates": gates, "section_mix": mix}


# ---------------------------------------------------------------- coverage
def find_term(term, text):
    """Return 'exact', 'variant' or None."""
    if CJK.search(term):
        if term in text:
            return "exact"
        return "variant" if norm(term) in norm(text) else None
    if re.search(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", text, re.I):
        return "exact"
    base = term[:-1] if len(term) > 4 and term.endswith("s") and not term.endswith("ss") else term
    if re.search(r"(?<![A-Za-z0-9])" + re.escape(base) + r"(?:s|es|ed|ing)?(?![A-Za-z0-9])", text, re.I):
        return "exact"
    return "variant" if norm(base) and norm(base) in norm(text) else None


def coverage(posting_text, cv_text, top):
    terms = analyse(posting_text)["terms"][:top]
    cv_lines = [l for l in cv_text.splitlines() if l.strip()]
    skim_zone = "\n".join(cv_lines[: max(1, len(cv_lines) // 3)])
    rows, got, possible = [], 0.0, 0.0
    for t in terms:
        hit = find_term(t["term"], cv_text)
        in_skim = bool(find_term(t["term"], skim_zone)) if hit else False
        possible += t["score"]
        if hit == "exact":
            got += t["score"]
        elif hit == "variant":
            got += t["score"] * 0.5
        rows.append({**t, "match": hit or "missing", "in_top_third": in_skim})
    pct = round(100 * got / possible) if possible else 0
    return {"weighted_coverage_pct": pct, "rows": rows}


# ---------------------------------------------------------------- lint
GENERIC_EN = [
    "results-driven", "results driven", "team player", "passionate about", "hard-working", "hardworking",
    "detail-oriented", "self-starter", "go-getter", "synergy", "think outside the box", "proven track record",
    "excellent communication skills", "strong communication skills", "fast-paced environment", "wear many hats",
    "i am writing to apply", "i am excited to apply", "i believe i would be a great fit", "perfect fit",
    "dynamic", "leverage", "utilize", "cutting-edge", "seamless", "robust", "world-class", "best-in-class",
    "thrilled", "delve", "tapestry", "testament to", "in today's", "ever-evolving", "game-changer", "rockstar",
    "ninja", "guru", "go above and beyond", "hit the ground running", "unique opportunity", "make an impact",
]
GENERIC_ZH = [
    "热爱", "积极主动", "抗压能力强", "学习能力强", "团队合作精神", "吃苦耐劳", "认真负责", "沟通能力强",
    "具有良好的", "责任心强", "赋能", "抓手", "闭环", "底层逻辑", "深耕", "极致", "全方位", "多维度",
    "颗粒度", "打通", "助力", "高度契合", "非常荣幸", "贵公司", "一直以来", "综上所述",
]
WEAK_OPENERS = re.compile(r"^(?:responsible for|worked on|helped|assisted|involved in|participated in|tasked with|"
                          r"duties included|in charge of|负责|参与|协助|配合|帮助)", re.I)
PLACEHOLDER = re.compile(r"\[(?:NEED|TODO|TBD|待补|待确认)[^\]]*\]|\bTODO\b|\bXX+\b|某某", re.I)
BULLET = re.compile(r"^\s*(?:[-*•·]|\d+[.)、])\s+")
NUMBER = re.compile(r"\d|%|percent|[一二三四五六七八九十百千万亿两]+(?:个|倍|万|人|家|次|项|天|周|月|年)")


def measure(text):
    cjk = len(CJK.findall(text))
    words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'+#.-]*", text))
    return words, cjk


def lint(text, max_words=None):
    issues = []
    low = text.lower()
    for phrase in GENERIC_EN:
        n = len(re.findall(r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", low))
        if n:
            issues.append({"kind": "generic", "detail": phrase, "count": n})
    for phrase in GENERIC_ZH:
        n = text.count(phrase)
        if n:
            issues.append({"kind": "generic", "detail": phrase, "count": n})
    for i, line in enumerate(text.splitlines(), 1):
        if PLACEHOLDER.search(line):
            issues.append({"kind": "placeholder", "line": i, "detail": line.strip()[:80]})
        if not BULLET.match(line):
            continue
        body = BULLET.sub("", line).strip()
        if WEAK_OPENERS.match(body):
            issues.append({"kind": "duty-not-result", "line": i, "detail": body[:80]})
        if not NUMBER.search(body):
            issues.append({"kind": "no-number", "line": i, "detail": body[:80]})
        w, c = measure(body)
        if w > 32 or c > 70:
            issues.append({"kind": "long-bullet", "line": i, "detail": f"{w} words / {c} CJK chars"})
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    i_start = sum(1 for s in sentences if re.match(r"^I\b", s))
    if len(sentences) >= 5 and i_start / len(sentences) > 0.4:
        issues.append({"kind": "i-heavy", "detail": f"{i_start}/{len(sentences)} sentences start with 'I'"})
    dashes = text.count("—")
    if dashes >= 3:
        issues.append({"kind": "dash-habit", "detail": f"{dashes} em dashes"})
    words, cjk = measure(text)
    size = words + (cjk + 1) // 2  # rough: two CJK characters read like one English word
    if max_words and size > max_words:
        issues.append({"kind": "over-budget", "detail": f"~{size} word-equivalents > {max_words}"})
    return {"words": words, "cjk_chars": cjk, "word_equivalents": size, "issues": issues}


# ---------------------------------------------------------------- output
def print_signals(r, top):
    if r.get("title"):
        print(f"TITLE: {r['title']}  (mirror this wording in your headline if it is true)\n")
    print("REQUIREMENT SIGNALS (higher = stated harder, earlier, more often)")
    print(f"{'score':>6}  {'n':>2}  term  [sections]")
    for t in r["terms"][:top]:
        print(f"{t['score']:>6}  {t['count']:>2}  {t['term']}  [{', '.join(t['sections'])}]")
    print("\nHARD GATES (check these before writing anything)")
    if not r["gates"]:
        print("  none detected; still read the posting for location, visa and seniority")
    for g in r["gates"]:
        tag = " (softened)" if g["soft"] else (" (offered, from benefits)" if g["in_benefits"] else "")
        print(f"  - {g['type']}{tag}: {g['line'][:100]}")
    print("\nSECTION MIX (share of non-empty lines)")
    print("  " + "  ".join(f"{k}={v}" for k, v in r["section_mix"].items()))
    if r["section_mix"].get("noise", 0) > 0.4:
        print("  note: mostly boilerplate; the real signal is thin, so lean on the probe step")


def print_coverage(r):
    print(f"WEIGHTED COVERAGE: {r['weighted_coverage_pct']}%  (exact = full credit, variant spelling = half)")
    print(f"{'score':>6}  {'match':<8} top⅓  term")
    for row in r["rows"]:
        mark = "yes" if row["in_top_third"] else "-"
        print(f"{row['score']:>6}  {row['match']:<8} {mark:<4}  {row['term']}")
    missing = [x["term"] for x in r["rows"] if x["match"] == "missing"]
    if missing:
        print("\nMISSING, heaviest first. Add only where you can point to real proof:")
        print("  " + ", ".join(missing[:12]))
    variants = [x["term"] for x in r["rows"] if x["match"] == "variant"]
    if variants:
        print("SPELLED DIFFERENTLY from the posting (use their exact form once):")
        print("  " + ", ".join(variants[:12]))


def print_lint(r):
    print(f"SIZE: {r['words']} words, {r['cjk_chars']} CJK chars (~{r['word_equivalents']} word-equivalents)")
    if not r["issues"]:
        print("CLEAN: no generic phrases, duty bullets, missing numbers or placeholders found.")
        return
    order = ["placeholder", "generic", "duty-not-result", "no-number", "long-bullet", "i-heavy", "dash-habit", "over-budget"]
    for kind in order:
        group = [x for x in r["issues"] if x["kind"] == kind]
        if not group:
            continue
        print(f"\n{kind.upper()} ({len(group)})")
        for x in group:
            where = f"L{x['line']}: " if "line" in x else ""
            extra = f" x{x['count']}" if x.get("count", 1) > 1 else ""
            print(f"  - {where}{x['detail']}{extra}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("signals", help="rank requirement terms and list hard gates")
    s.add_argument("posting")
    s.add_argument("--top", type=int, default=25)
    c = sub.add_parser("coverage", help="check a CV against the posting's weighted terms")
    c.add_argument("posting")
    c.add_argument("cv")
    c.add_argument("--top", type=int, default=25)
    l = sub.add_parser("lint", help="flag generic, duty-style or unproven lines in a draft")
    l.add_argument("draft")
    l.add_argument("--max", type=int, dest="max_words")
    l.add_argument("--strict", action="store_true", help="exit 1 when any issue is found")
    for p in (s, c, l):
        p.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.cmd == "signals":
        r = analyse(read(a.posting))
        r["terms"] = r["terms"][: a.top]
        print(json.dumps(r, ensure_ascii=False, indent=2)) if a.json else print_signals(r, a.top)
    elif a.cmd == "coverage":
        r = coverage(read(a.posting), read(a.cv), a.top)
        print(json.dumps(r, ensure_ascii=False, indent=2)) if a.json else print_coverage(r)
    else:
        r = lint(read(a.draft), a.max_words)
        print(json.dumps(r, ensure_ascii=False, indent=2)) if a.json else print_lint(r)
        if a.strict and r["issues"]:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
