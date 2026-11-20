# 金融经济论文选刊 Skill

给金融、经济学及相邻的会计、管理、公共政策论文做期刊选择：候选召回、适配比较、投稿排序、材料合规检查、拒稿后改投。

核心不是"推荐一个影响因子高的刊"，而是把**事实、判断和未知**分开：先把硬门槛（scope、刊型、语言、院校认定、预算、数据政策）逐项核成 `通过 / 不通过 / 未知`，再谈适配度与投稿顺序。

## 为什么需要它

选刊最常见的三种塌方：拿第三方标签当官方认定、把搜索摘要当投稿政策、把综述里的录用率折算成"我这篇的概率"。这个 Skill 的每条规则都在拦这三件事：

- 评级体系不互换（CSSCI 来源 ≠ 北大核心 ≠ AMI 核心；JCR 分区 ≠ 中科院分区）
- 缺失不当通过，未知不写成"可投"
- 不预测单篇录用概率，不承诺保底或按时见刊
- 索引里的标签只是线索，任何评级陈述必须带官方名单版本与核实日期

## 能力构成

| 能力 | 实现 | 说明 |
|---|---|---|
| 候选召回 | `data/journal-venues.json` + `scripts/venue_index.py` | 213 条中英刊名索引（107 国际 + 106 中文），按刊名/中文别名/学科/地区/标签检索 |
| 适配比较 | `scripts/score_candidates.py` | 透明权重、缺失不记 0、覆盖率预警、权重 ±20% 扰动输出名次区间 |
| 中文体系辨析 | `references/cn-journal-systems.md` | CSSCI/北大核心/AMI/CSCD/中科院分区/JCR 的口径与核验入口 |
| 投稿材料合规 | `references/submission-package.md` + `templates/submission-plan.template.json` | 英中刊分列清单，状态四值：已备/待补/不适用/未知 |
| 改投决策 | `references/resubmission-decision.md` | 拒稿类型定性 → 修复/换定位/降档，含时间账写法 |
| 发布自检 | `scripts/selftest.py` | 索引完整性、脚本行为、模板合法性、主题一致性 |

## 目录结构

```
SKILL.md                          主流程（六阶段）
README.md                         本文件
CHANGELOG.md                      v1.0 → v2.0 变更
THIRD-PARTY-NOTICE.md             派生数据的 MIT 授权
data/journal-venues.json          刊名索引（只做召回，不做评级）
references/                       9 份规范
scripts/                          venue_index / score_candidates / selftest
templates/                        shortlist / submission-plan
examples/                         评分脚本示例（全员虚构刊名）
agents/, assets/                  运行配置与图标
```

## 安装

把本仓库作为 Skill 目录安装到支持 Skills 的环境，目录名与 `SKILL.md` 里的 `name` 保持一致：

```bash
git clone https://github.com/ZHYJY/select-finance-econ-journals.git
cp -r select-finance-econ-journals <你的 skills 目录>/select-finance-econ-journals
```

只需要 Python 3.9+，无第三方依赖。

## 用法

```bash
# 查索引
python scripts/venue_index.py --query 金融 --limit 12
python scripts/venue_index.py --discipline finance --region china
python scripts/venue_index.py --label CSSCI --discipline accounting
python scripts/venue_index.py --validate

# 比较候选（先按 templates/shortlist.template.json 准备 candidates）
python scripts/score_candidates.py examples/candidates.example.json --perturb 200

# 发布前自检
python scripts/selftest.py
```

调用示例：

> 这篇中国上市公司 ESG 与融资成本的 DiD，样本 2010–2023，商业数据库不能再分发。我 2027 年 6 月毕业，学院认 CSSCI 来源和 SSCI 二区以上，预算 1 万以内。帮我选刊并给投稿顺序。

## 数据边界

`data/journal-venues.json` 只用于"想得起有哪些刊"，不是评级表：

- 不含影响因子、分区、APC、审稿周期、录用率——这些必须现查
- 约六成条目无标签，`labels` 为空不代表该刊没档次
- 部分中文刊以英文官方刊名登记（`Economic Research Journal` 即《经济研究》），中文检索靠 `aliases` 字段
- `Journal of Financial Research` 在此指《金融研究》，与美国同名刊不是同一本，须用 ISSN 区分
- 投稿前必须核对刊名全称与是否改名、ISSN 是否对应同一实体

## 第三方数据

索引的上游部分派生自 [Awesome-Journal-Skills](https://github.com/brycewang-stanford/Awesome-Journal-Skills)（MIT License, Copyright (c) 2026 Bryce Wang），仅提取刊名、学科、地区与指示性分档字段。许可全文见 `THIRD-PARTY-NOTICE.md`。

## 声明

本 Skill 只提供选刊建议，不自动投稿、不付费、不联系编辑、不上传未发表稿件。所有政策与评级结论以官方当期文件为准。
