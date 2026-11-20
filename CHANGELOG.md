# 更新记录

## v2.0 — 2026-11-20

在 v1.0 的“核实事实、三值硬门槛、不预测录用率”框架上做能力扩展，不改变其核心判断纪律。

**新增**

- `data/journal-venues.json`：213 条中英刊名索引（107 条国际刊 + 106 条中文刊），用于召回、命名统一与去重；不含影响因子、分区、APC、审稿周期。含 15 条中文别名（部分中文刊在上游以英文官方刊名登记）。
- `scripts/venue_index.py`：索引查询与完整性校验（按刊名/学科/地区/标签筛选，`--validate` 检查 schema、重复 id、重复刊名、非法取值）。
- `scripts/score_candidates.py`：透明加权比较。缺失项不记 0、单独报告覆盖率、覆盖率低于 60% 不给排序、权重 ±20% 扰动输出名次区间。
- `scripts/selftest.py`：离线自检索引、脚本、模板与主题一致性，发布前必跑。
- `references/cn-journal-systems.md`：CSSCI / 北大核心 / AMI / CSCD / 中科院分区 / JCR 的口径区分、版本要求与核验入口。
- `references/submission-package.md`：英文刊与中文刊的投稿材料清单与合规检查项。
- `references/resubmission-decision.md`：拒稿类型定性 → 修复/换定位/降档的决策树与时间账写法。
- `references/venue-index.md`：索引字段含义、可信度与使用纪律。
- `templates/shortlist.template.json`、`templates/submission-plan.template.json`：机器可读的短名单与投稿包。
- `examples/candidates.example.json`：评分脚本的可运行示例（全员虚构刊名）。
- `THIRD-PARTY-NOTICE.md`：上游 MIT 数据授权与再分发要求。
- `README.md`：仓库说明。

**修改**

- `SKILL.md` 重构为六阶段流程（画像 → 召回 → 核验 → 比较 → 中文专项 → 材料与改投），把脚本入口写进主流程。
- `references/sources.md` 增补 5 个同类项目的取舍，并说明本地数据授权。
- `references/evaluation-cases.md` 增补 7 个边界场景（体系口径追问、索引标签误用、中英文先后发表、覆盖率差异、权重扰动等）。

**保持不变**

- 不预测单篇录用概率，不承诺保底或按时见刊。
- 硬门槛三值判定：不通过排除、未知列条件候选、全部通过才可执行。
- 不自动投稿、不付费、不联系编辑、不上传未发表稿件。
- 评级体系之间不换算，缺失不当通过。

**已知限制**

- 索引标签不完整（约六成条目无标签）且非官方等级，只能做线索。
- 部分中文刊在上游以英文官方刊名登记（如 `Economic Research Journal` 即《经济研究》），已补 15 条中文别名；未覆盖的中文刊仍需按官网检索。
- `Journal of Financial Research` 在索引中指《金融研究》，与美国同名刊不属同一本，须用 ISSN 区分。
- 脚本只校验结构与逻辑，不代表任何期刊的当期政策已核实。
