#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""候选期刊的透明加权比较与权重敏感性检验。

设计约束：
- 缺失（证据不足/未知）不记为 0，不填中性值；只从分母中剔除，并单独报告覆盖率。
- 覆盖率过低（<0.6）不给排序结论，只给"证据不足"。
- 硬门槛未通过的候选不进入排序，单独列为排除项。
- 输出是决策辅助，不是录用概率。

用法：
    python scripts/score_candidates.py path/to/candidates.json
    python scripts/score_candidates.py path/to/candidates.json --perturb 200 --top 3
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

DEFAULT_CRITERIA = ("读者适配", "贡献与定位", "方法与证据", "硬约束满足度", "改稿成本")

SCALE = {"强": 3.0, "中": 2.0, "弱": 1.0, "strong": 3.0, "medium": 2.0, "weak": 1.0}
MISSING_TOKENS = {"", None, "证据不足", "未知", "unknown", "缺失", "未核实"}

CONFIDENCE_THRESHOLD = 0.6
STRONG_COVERAGE = 0.8


def label_to_value(raw) -> float | None:
    if raw is None:
        return None
    key = str(raw).strip()
    if key in MISSING_TOKENS:
        return None
    return SCALE.get(key)


def normalize_weights(criteria: tuple[str, ...], raw: dict | None) -> dict[str, float]:
    if not raw:
        return {c: 1.0 / len(criteria) for c in criteria}
    picked = {c: float(raw.get(c, 0.0)) for c in criteria}
    total = sum(picked.values())
    if total <= 0:
        raise ValueError("weights 之和必须大于 0")
    return {c: v / total for c, v in picked.items()}


def score_candidate(candidate: dict, weights: dict[str, float]) -> dict:
    ratings = candidate.get("ratings") or {}
    rated_weight = 0.0
    weighted_sum = 0.0
    missing: list[str] = []
    for criterion, weight in weights.items():
        value = label_to_value(ratings.get(criterion))
        if value is None:
            missing.append(criterion)
            continue
        rated_weight += weight
        weighted_sum += weight * value
    coverage = rated_weight  # weights 已归一化
    if rated_weight > 0:
        score = weighted_sum / rated_weight
    else:
        score = None
    if score is None:
        confidence = "无"
    elif coverage >= STRONG_COVERAGE:
        confidence = "高"
    elif coverage >= CONFIDENCE_THRESHOLD:
        confidence = "中"
    else:
        confidence = "低"
    return {
        "score": score,
        "coverage": coverage,
        "confidence": confidence,
        "missing": missing,
    }


def rank(rows: list[dict]) -> list[dict]:
    return sorted(
        rows,
        key=lambda r: (r["score"] is None, -(r["score"] or 0.0), r["name"]),
    )


def perturb_weights(weights: dict[str, float], rng: random.Random) -> dict[str, float]:
    bumped = {c: w * rng.uniform(0.8, 1.2) for c, w in weights.items()}
    total = sum(bumped.values())
    return {c: v / total for c, v in bumped.items()}


def analyze(payload: dict, perturb_runs: int, top_n: int, seed: int) -> dict:
    criteria = tuple(payload.get("criteria") or DEFAULT_CRITERIA)
    weights = normalize_weights(criteria, payload.get("weights"))
    candidates = payload.get("candidates") or []
    if not candidates:
        raise ValueError("candidates 为空")

    eligible, excluded, conditional = [], [], []
    eligible_raw: list[dict] = []
    for candidate in candidates:
        gate = str(candidate.get("gate_status") or "unknown").strip().lower()
        row = {
            "name": candidate.get("name") or "(未命名)",
            "gate": gate,
            "notes": candidate.get("notes") or "",
        }
        row.update(score_candidate(candidate, weights))
        if gate == "pass":
            eligible.append(row)
            eligible_raw.append(candidate)
        elif gate == "fail":
            excluded.append(row)
        else:
            conditional.append(row)

    ranked = rank(eligible)
    unknown_ranked = rank([r for r in conditional if r["score"] is not None])

    # 权重扰动：只看通过硬门槛的候选，统计名次波动
    stability: dict[str, dict] = {}
    if ranked and perturb_runs > 0:
        rng = random.Random(seed)
        history = {r["name"]: [] for r in ranked}
        for _ in range(perturb_runs):
            alt_weights = perturb_weights(weights, rng)
            alt_rows = []
            for candidate in eligible_raw:
                alt = score_candidate(candidate, alt_weights)
                alt["name"] = candidate.get("name") or "(未命名)"
                alt_rows.append(alt)
            for position, row in enumerate(rank(alt_rows), start=1):
                if row["score"] is not None:
                    history[row["name"]].append(position)
        for name, positions in history.items():
            if not positions:
                stability[name] = {"min": None, "max": None, "top_n_share": 0.0}
                continue
            in_top = sum(1 for p in positions if p <= top_n) / len(positions)
            stability[name] = {
                "min": min(positions),
                "max": max(positions),
                "top_n_share": round(in_top, 3),
            }

    return {
        "criteria": criteria,
        "weights": {c: round(w, 4) for c, w in weights.items()},
        "eligible": ranked,
        "conditional": unknown_ranked,
        "excluded": excluded,
        "stability": stability,
        "coverage_floor": CONFIDENCE_THRESHOLD,
        "perturb_runs": perturb_runs,
    }


def render(result: dict, top_n: int) -> str:
    lines: list[str] = []
    lines.append("权重（已归一化）:")
    for criterion, weight in result["weights"].items():
        lines.append(f"  {criterion}: {weight:.3f}")
    lines.append("")

    if result["eligible"]:
        lines.append(f"可执行候选排序（覆盖率下限 {result['coverage_floor']:.0%} 时置信度才为高中）:")
        lines.append(f"{'排名':<4}{'刊名':<44}{'加权分':<9}{'覆盖':<8}{'置信':<6}{'缺失项'}")
        for position, row in enumerate(result["eligible"], start=1):
            score = "—" if row["score"] is None else f"{row['score']:.2f}"
            missing = "、".join(row["missing"]) or "无"
            lines.append(
                f"{position:<4}{row['name'][:42]:<44}{score:<9}"
                f"{row['coverage']:.0%}{'':<4}{row['confidence']:<6}{missing}"
            )
    else:
        lines.append("没有通过全部硬门槛的候选。")

    if result["conditional"]:
        lines.append("")
        lines.append("条件候选（存在未知硬门槛，不能当作可投）:")
        for row in result["conditional"]:
            score = "—" if row["score"] is None else f"{row['score']:.2f}"
            lines.append(f"  {row['name']}  加权分={score}  置信={row['confidence']}")

    if result["excluded"]:
        lines.append("")
        lines.append("排除项（硬门槛不通过，声誉与适配度不能抵消）:")
        for row in result["excluded"]:
            lines.append(f"  {row['name']}" + (f"  ({row['notes']})" if row["notes"] else ""))

    if result["stability"]:
        lines.append("")
        lines.append(f"权重敏感性（±20% 扰动，{result['perturb_runs']} 次）:")
        for name, stat in result["stability"].items():
            if stat["min"] is None:
                lines.append(f"  {name}: 无有效评分，未做扰动")
            else:
                lines.append(
                    f"  {name}: 名次区间 {stat['min']}–{stat['max']}，"
                    f"留在前 {top_n} 的比例 {stat['top_n_share']:.0%}"
                )
        lines.append("若某个候选的名次区间跨度大，说明结论依赖权重设定，应降低排序的确定性表述。")

    lines.append("")
    lines.append("说明：加权分只反映当前证据下的适配度，不是录用概率。缺失项不记 0，覆盖率低的候选不构成排序依据。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="候选期刊透明加权比较")
    parser.add_argument("input", type=Path, help="候选 JSON 文件")
    parser.add_argument("--perturb", type=int, default=100, help="权重扰动次数（0 表示跳过）")
    parser.add_argument("--top", type=int, default=3, help="稳定性统计的前 N 名")
    parser.add_argument("--seed", type=int, default=20261120, help="扰动随机种子，保证可复现")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果")
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"找不到输入文件: {args.input}", file=sys.stderr)
        return 2

    with args.input.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    try:
        result = analyze(payload, args.perturb, args.top, args.seed)
    except ValueError as exc:
        print(f"输入有误: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result, args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
