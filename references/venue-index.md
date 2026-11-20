# 本地期刊索引的正确用法

`data/journal-venues.json` 是一份 213 条金融、经济、会计、管理、公共政策方向的刊名索引，用途只有一个：**召回候选、统一中英文刊名口径、去重**。

它**不是**评级表，也**不是**数据源。里面没有影响因子、分区、APC、审稿周期、录用率、页数限制——这些必须在投稿当时现查。

## 字段含义

| 字段 | 说明 | 可信度 |
|---|---|---|
| `id` | 内部稳定标识，用于去重与脚本引用 | 可靠 |
| `name` | 刊名（中文刊给中文名，国际刊给英文名） | 需按官网核对拼写与副标题 |
| `aliases` | 中文别名（部分中文刊在上游以英文官方刊名登记，此处补通行中译） | 需按官网核对 |
| `discipline` | 学科归属（如 `finance`、`economics/labor`） | 粗分类，仅用于筛方向 |
| `region` | `china` / `international` | 大体可靠，上游有少量错标 |
| `tier_bucket` | 上游目录的指示性分档（如 `top-3 finance`、`field`） | **不可引用**，需核实 |
| `labels` | 上游标签（如 `SSCI`、`CSSCI`、`FT50`） | **不完整且非官方**，约六成条目为空，需核实 |
| `source` | `awesome-journal-skills-catalog` 或 `curated` | 见 `THIRD-PARTY-NOTICE.md` |

## 两个已知陷阱

- **中文刊用英文题名登记**：`Economic Research Journal` 是《经济研究》，`Journal of Management World` 是《管理世界》。检索中文名靠 `aliases`，不要以为索引里没有这本刊。
- **同名不同刊**：索引里的 `Journal of Financial Research` 指《金融研究》（中国），不是美国 Wiley 出版的 *Journal of Financial Research*。类似情况必须用 ISSN 或主办单位区分，不能只凭刊名。

## 查询方式

用脚本查，不要靠记忆列刊名：

```bash
python scripts/venue_index.py --list-disciplines
python scripts/venue_index.py --query 金融 --limit 12
python scripts/venue_index.py --discipline finance --region china --limit 15
python scripts/venue_index.py --label CSSCI --discipline accounting
python scripts/venue_index.py --validate
```

检索是字符串包含匹配，`--query` 同时作用于刊名与 id。中文与英文均可。

## 使用纪律

1. **索引只用于"想得起有哪些刊"**：候选池必须在索引之外补充——参考文献、近期同题材论文、学会与出版社官网、导师与同行建议。只用索引召回会系统性漏刊。
2. **索引里的刊名不能直接写进交付物**：要按官网核对全称、副标题、是否改名（期刊改名很常见，旧名与新名可能同时索引）。
3. **索引里的标签不能当结论**：`labels` 为空不代表该刊没档次，`labels` 有值也不代表当期仍在该名单。任何"这本刊是 FT50 / CSSCI / ABS 4*"的陈述，都必须带官方名单版本与核实日期。
4. **缺失即未知**：索引没有的刊不是不存在，是没被收录。不要因为查不到就排除，也不要因为查得到就当已核实。
5. **去重口径**：同一刊可能有缩写、旧名、中文译名。以 ISSN 或官网刊名为准，索引 id 只在本 Skill 内部一致。

## 维护

- 更新上游目录时重跑派生流程，保留 `provenance` 与 `generated_at`。
- 手补条目（`source: "curated"`）只允许写刊名与学科，不得写入任何评级或计量数字。
- 每次维护后运行 `python scripts/selftest.py`，确认 schema、条数与查询行为均正常。
