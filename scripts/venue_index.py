#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地期刊索引查询工具。

用途：从 data/journal-venues.json 召回候选刊、按学科/地区/标签筛选、检查索引完整性。
不提供任何影响因子、分区、APC、审稿周期等易变数据——这些必须实时核实。

用法：
    python scripts/venue_index.py --list-disciplines
    python scripts/venue_index.py --query 金融 --limit 12
    python scripts/venue_index.py --discipline finance --region china
    python scripts/venue_index.py --label CSSCI --discipline accounting
    python scripts/venue_index.py --validate
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_VENUE_FIELDS = ("id", "name", "discipline", "region", "source")
VALID_REGIONS = ("china", "international")
VALID_SOURCES = ("awesome-journal-skills-catalog", "curated")


def default_data_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "journal-venues.json"


def load_index(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_index(doc: dict) -> list[str]:
    """返回问题清单，空列表表示通过。"""
    problems: list[str] = []

    for key in ("schema_version", "generated_at", "provenance", "disclaimer", "venues"):
        if key not in doc:
            problems.append(f"缺少顶层字段: {key}")

    venues = doc.get("venues") or []
    if not isinstance(venues, list) or not venues:
        problems.append("venues 必须是非空数组")
        return problems

    declared = doc.get("venue_count")
    if declared != len(venues):
        problems.append(f"venue_count={declared} 与实际条数 {len(venues)} 不一致")

    ids: set[str] = set()
    names: dict[str, int] = {}
    for idx, venue in enumerate(venues):
        for field in REQUIRED_VENUE_FIELDS:
            if field not in venue:
                problems.append(f"第 {idx} 条缺少字段 {field}")
        vid = venue.get("id")
        if vid:
            if vid in ids:
                problems.append(f"重复 id: {vid}")
            ids.add(vid)
        name = venue.get("name")
        if name:
            names[name] = names.get(name, 0) + 1
        if venue.get("region") not in VALID_REGIONS:
            problems.append(f"{vid}: region 非法 ({venue.get('region')})")
        if venue.get("source") not in VALID_SOURCES:
            problems.append(f"{vid}: source 非法 ({venue.get('source')})")
        labels = venue.get("labels")
        if labels is not None and not isinstance(labels, list):
            problems.append(f"{vid}: labels 必须是数组")
        aliases = venue.get("aliases")
        if aliases is not None and not isinstance(aliases, list):
            problems.append(f"{vid}: aliases 必须是数组")

    for name, count in names.items():
        if count > 1:
            problems.append(f"重复刊名: {name} ({count} 次)")

    # 手补条目不得携带任何评级或计量字段
    forbidden = {"impact_factor", "apc", "acceptance_rate", "review_time", "quartile", "issn"}
    for venue in venues:
        if venue.get("source") == "curated":
            hit = forbidden & set(venue)
            if hit:
                problems.append(f"{venue.get('id')}: curated 条目含禁止字段 {sorted(hit)}")

    return problems


def filter_venues(
    venues: list[dict],
    query: str | None = None,
    discipline: str | None = None,
    region: str | None = None,
    label: str | None = None,
) -> list[dict]:
    result = []
    q = (query or "").strip().lower()
    for venue in venues:
        if q:
            name = venue.get("name", "")
            aliases = " ".join(str(x) for x in (venue.get("aliases") or []))
            haystack = f"{name} {venue.get('id', '')} {aliases}".lower()
            if q not in haystack:
                continue
        if discipline:
            d = (venue.get("discipline") or "").lower()
            if not (d == discipline.lower() or d.startswith(discipline.lower() + "/")):
                continue
        if region and venue.get("region") != region:
            continue
        if label:
            labels = [str(x).lower() for x in (venue.get("labels") or [])]
            if label.lower() not in labels:
                continue
        result.append(venue)
    return result


def format_row(venue: dict) -> str:
    labels = ", ".join(venue.get("labels") or []) or "—"
    tier = venue.get("tier_bucket") or "—"
    aliases = venue.get("aliases") or []
    alias = f"  别名={', '.join(aliases)}" if aliases else ""
    return (
        f"{venue.get('name','')}  [{venue.get('region')}]  "
        f"{venue.get('discipline')}  tier={tier}  labels={labels}{alias}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="查询本地期刊索引（仅用于召回与去重）")
    parser.add_argument("--data", type=Path, default=None, help="索引文件路径")
    parser.add_argument("--query", "-q", default=None, help="按刊名或 id 做包含匹配")
    parser.add_argument("--discipline", "-d", default=None, help="学科，如 finance、economics/labor")
    parser.add_argument("--region", "-r", choices=VALID_REGIONS, default=None, help="地区")
    parser.add_argument("--label", "-l", default=None, help="标签，如 CSSCI、FT50")
    parser.add_argument("--limit", "-n", type=int, default=20, help="最多显示条数")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    parser.add_argument("--list-disciplines", action="store_true", help="列出索引中的学科分布")
    parser.add_argument("--validate", action="store_true", help="校验索引完整性")
    args = parser.parse_args(argv)

    path = args.data or default_data_path()
    if not path.exists():
        print(f"找不到索引文件: {path}", file=sys.stderr)
        return 2

    doc = load_index(path)

    if args.validate:
        problems = validate_index(doc)
        print(f"文件: {path}")
        print(f"条数: {len(doc.get('venues', []))}  声明: {doc.get('venue_count')}")
        print(f"生成日期: {doc.get('generated_at')}  版本: {doc.get('schema_version')}")
        if problems:
            print(f"发现 {len(problems)} 个问题:")
            for item in problems:
                print(f"  - {item}")
            return 1
        print("校验通过：schema、id、刊名唯一性、region/source 取值、hand-curated 字段约束均正常。")
        print("注意：本索引不含影响因子、分区、APC、审稿周期，任何评级引用都必须现查官方名单。")
        return 0

    if args.list_disciplines:
        counts: dict[str, int] = {}
        for venue in doc.get("venues", []):
            key = venue.get("discipline") or "unknown"
            counts[key] = counts.get(key, 0) + 1
        for key, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"{count:>4}  {key}")
        return 0

    venue_list = doc.get("venues", [])
    selected = filter_venues(
        venue_list,
        query=args.query,
        discipline=args.discipline,
        region=args.region,
        label=args.label,
    )

    if args.json:
        print(json.dumps(selected, ensure_ascii=False, indent=2))
        return 0

    total = len(selected)
    print(f"命中 {total} 条（显示前 {min(args.limit, total)} 条）")
    if total == 0:
        print("没有命中。索引并非全集：请改用参考文献、近期论文与官网继续召回。")
        return 0
    for venue in selected[: args.limit]:
        print("  " + format_row(venue))
    if total > args.limit:
        print(f"... 还有 {total - args.limit} 条，可用 --limit 调整")
    print("提示：labels/tier_bucket 来自第三方目录且不完整，不得直接写进结论。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
