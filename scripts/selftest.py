#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""离线自检：索引完整性、查询行为、评分脚本、模板与文档结构。

不联网、不依赖第三方库。用于发布前与每次维护后确认 Skill 可用。

用法：
    python scripts/selftest.py
    python scripts/selftest.py --verbose
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import score_candidates  # noqa: E402
import venue_index  # noqa: E402

REQUIRED_REFERENCES = (
    "cn-journal-systems.md",
    "domain-fit.md",
    "evaluation-cases.md",
    "output-template.md",
    "resubmission-decision.md",
    "sources.md",
    "submission-package.md",
    "venue-index.md",
    "verification.md",
)

REQUIRED_TEMPLATES = ("shortlist.template.json", "submission-plan.template.json")
REQUIRED_EXAMPLES = ("candidates.example.json",)

# 本 Skill 是选刊主题；以下文件若出现说明打包时混入了分镜视频 Skill 的内容
STALE_DIRS = (
    "references/asset-lock.md",
    "references/character-bible.md",
    "references/adaptive-platform.md",
    "references/shot-continuity.md",
    "scripts/adapt.py",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_frontmatter(problems: list[str]) -> None:
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        problems.append("缺少 SKILL.md")
        return
    text = read_text(skill_md)
    if not text.startswith("---"):
        problems.append("SKILL.md 缺少 YAML frontmatter")
        return
    head = text.split("---", 2)[1]
    if "name:" not in head:
        problems.append("frontmatter 缺少 name")
    if "description:" not in head:
        problems.append("frontmatter 缺少 description")
    if "select-finance-econ-journals" not in head:
        problems.append("frontmatter name 与目录名不一致")


def test_references(problems: list[str]) -> None:
    ref_dir = SKILL_DIR / "references"
    for name in REQUIRED_REFERENCES:
        path = ref_dir / name
        if not path.exists():
            problems.append(f"缺少 references/{name}")
        elif len(read_text(path).strip()) < 200:
            problems.append(f"references/{name} 内容过短，可能未写完")


def test_templates(problems: list[str]) -> None:
    for name in REQUIRED_TEMPLATES:
        path = SKILL_DIR / "templates" / name
        if not path.exists():
            problems.append(f"缺少 templates/{name}")
            continue
        try:
            data = json.loads(read_text(path))
        except json.JSONDecodeError as exc:
            problems.append(f"templates/{name} 不是合法 JSON: {exc}")
            continue
        if "schema_version" not in data:
            problems.append(f"templates/{name} 缺少 schema_version")


def test_index(problems: list[str], verbose: bool) -> None:
    path = venue_index.default_data_path()
    if not path.exists():
        problems.append(f"缺少索引文件 {path}")
        return
    doc = venue_index.load_index(path)
    for item in venue_index.validate_index(doc):
        problems.append(f"index: {item}")
    if len(doc.get("venues", [])) < 100:
        problems.append("索引条数少于 100，疑似被截断")

    checks = (
        ({"query": "金融"}, "按中文关键词检索"),
        ({"discipline": "finance", "region": "china"}, "按学科+地区检索"),
        ({"label": "CSSCI"}, "按标签检索"),
        ({"query": "Journal of Finance"}, "按英文刊名检索"),
    )
    for kwargs, label in checks:
        hits = venue_index.filter_venues(doc["venues"], **kwargs)
        if not hits:
            problems.append(f"查询失效: {label} ({kwargs}) 无命中")
        elif verbose:
            print(f"    {label}: {len(hits)} 条")


def test_scoring(problems: list[str], verbose: bool) -> None:
    example = SKILL_DIR / "examples" / "candidates.example.json"
    if not example.exists():
        problems.append("缺少 examples/candidates.example.json")
        return
    payload = json.loads(read_text(example))
    result = score_candidates.analyze(payload, perturb_runs=50, top_n=3, seed=20261120)

    if len(result["eligible"]) != 2:
        problems.append(f"评分脚本硬门槛分流异常: eligible={len(result['eligible'])}")
    if len(result["excluded"]) != 1:
        problems.append(f"评分脚本未正确排除 fail 候选: excluded={len(result['excluded'])}")
    if len(result["conditional"]) != 1:
        problems.append(f"评分脚本未正确单列 unknown 候选: conditional={len(result['conditional'])}")

    for row in result["eligible"]:
        if row["score"] is None:
            problems.append(f"候选 {row['name']} 无有效评分")
        if "方法与证据" in row["missing"] and row["coverage"] >= 1.0:
            problems.append(f"候选 {row['name']} 缺失项未从覆盖率中剔除")

    # 缺失不得被当作 0 分：B 刊有 1 项缺失，加权分应高于"按 0 计"的结果
    eligible = {row["name"]: row for row in result["eligible"]}
    b = next((v for k, v in eligible.items() if "示例刊 B" in k), None)
    if b is None:
        problems.append("未找到示例刊 B")
    else:
        ratings = payload["candidates"][1]["ratings"]
        weights = score_candidates.normalize_weights(
            tuple(payload["criteria"]), payload.get("weights")
        )
        zero_filled = sum(
            weights[c] * (score_candidates.label_to_value(ratings.get(c)) or 0.0)
            for c in weights
        )
        if b["score"] is not None and b["score"] <= zero_filled:
            problems.append("缺失项疑似被按 0 分计入（加权分未抬高）")

    # 权重扰动必须真的产出名次区间，否则说明扰动循环没拿到评分
    if not result["stability"]:
        problems.append("未产出权重敏感性结果")
    else:
        dead = [n for n, s in result["stability"].items() if s["min"] is None]
        if dead:
            problems.append(f"权重敏感性未产出有效名次: {dead}")

    if verbose:
        print(f"    可执行候选 {len(result['eligible'])}，条件候选 {len(result['conditional'])}，排除 {len(result['excluded'])}")


def test_scope(problems: list[str], verbose: bool) -> None:
    """确认 Skill 主题已从分镜视频改为选刊，没有残留的旧主题文件。"""
    for stale in STALE_DIRS:
        if (SKILL_DIR / stale).exists():
            problems.append(f"残留旧主题文件: {stale}")
    skill_md = read_text(SKILL_DIR / "SKILL.md")
    if "选刊" not in skill_md:
        problems.append("SKILL.md 未体现选刊主题")
    assets_icon = SKILL_DIR / "assets" / "icon.svg"
    if not assets_icon.exists():
        problems.append("缺少 assets/icon.svg")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="选刊 Skill 离线自检")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    problems: list[str] = []
    print(f"自检目录: {SKILL_DIR}")

    print("[1/6] SKILL.md frontmatter")
    test_frontmatter(problems)
    print("[2/6] references 完整性")
    test_references(problems)
    print("[3/6] templates 合法性")
    test_templates(problems)
    print("[4/6] 期刊索引")
    test_index(problems, args.verbose)
    print("[5/6] 评分脚本")
    test_scoring(problems, args.verbose)
    print("[6/6] 主题一致性")
    test_scope(problems, args.verbose)

    print()
    if problems:
        print(f"FAIL：{len(problems)} 个问题")
        for item in problems:
            print(f"  - {item}")
        return 1
    print("PASS：结构、索引、评分与主题一致性检查全部通过。")
    print("提醒：自检只验证数据与代码逻辑，不代表任何期刊的当期政策已核实。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
