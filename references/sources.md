# 参考来源与维护边界

设计核查日：2026-10-23（America/Los_Angeles）。链接是证据入口，不是永久有效的费用、评级、时长或期刊数据库；每次选刊重新核验。

## 现有skills与取舍

本版独立撰写，参考公开项目的能力与局限，不打包、执行或逐字复制其实现，不声称原作者背书。未来复用实现前核对当时版本和许可。

| 项目 | 参考方向 | 本版取舍 |
|---|---|---|
| [Auto-Empirical-Research-Skills / journal-selection](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/blob/main/skills/60-regisely-superpapers/skills/journal-selection/SKILL.md) | 实时scope、多层候选 | 不沿用示例费率时长，不凭单一名录判风险。 |
| [zero565656 / journal-recommender](https://github.com/zero565656/journal-recommender/blob/main/SKILL.md) | 分区、成本、风险核查 | 不从摘要推CAS档次，不强制先问再搜，不按分区上下一级机械推荐。 |
| [Awesome-Journal-Skills / Journal-Match](https://github.com/brycewang-stanford/Awesome-Journal-Skills/blob/main/shared-resources/journal-selection/journal-match.md) | 画像、方法、跨刊与改投 | 不依赖外部索引，不把总体接受率转单篇概率，不默认独立或机械降档。 |
| [keros68 / sci-select历史入口](https://github.com/keros68/sci-select)；[维护入口](https://github.com/keros68/xiaoyu-skill/tree/main/skills/sci-select) | 区分方向、层级、证据与未知 | 历史仓库已归档并声明迁移；维护入口正文获取未成功，不宣称审阅当前实现。不安装额外数据库/API，补充金融经济方法。 |
| [brycewang-stanford / Awesome-Journal-Skills](https://github.com/brycewang-stanford/Awesome-Journal-Skills)（MIT） | 200+ 期刊技能包与 `catalog.json` 刊名目录 | **仅取刊名、学科与地区做召回索引**，见下节授权说明；不复制其期刊策略正文，不沿用其指示性分档作为评级。 |
| [Wayne2ai / sci-journal-selection-skill](https://github.com/Wayne2ai/sci-journal-selection-skill) | 分区/预警名单/年度先例的组织方式 | 不采用其以分区为核心的推荐逻辑；金融经济刊的适配判断优先于分区。 |
| [hujizhou35-cmd / medical-journal-selector](https://github.com/hujizhou35-cmd/medical-journal-selector) | 医学刊的四分位+周期+适配对比结构 | 领域不同不迁移结论；只借鉴“把周期与适配并列呈现”的表达。 |
| [rong0000g / paper-forge](https://github.com/rong0000g/paper-forge) | 选刊与投稿前检查合并的流程 | 不并入其写作与审稿模块，本 Skill 只负责选刊与改投。 |

## 本地数据授权

`data/journal-venues.json` 的 212 条上游条目派生自 Awesome-Journal-Skills 的 `catalog.json`（MIT License, Copyright (c) 2026 Bryce Wang），只保留 `id / name / discipline / region / tier_bucket / labels / lane` 七个字段，不含其期刊策略正文。另 12 条为手补中文刊，仅有刊名与学科。完整许可文本与再分发说明见仓库根目录 `THIRD-PARTY-NOTICE.md`。

该索引的作用边界：召回与命名统一。影响因子、分区、APC、审稿周期、录用率一律不内置，必须现查。

## 官方查询入口

- AEA：[JEL Guide](https://www.aeaweb.org/jel/guide/jel.php)、[Data and Code Policy](https://www.aeaweb.org/journals/data/data-code-policy)。后者有非公开数据处理要求，不据此一概排除商业/行政数据。
- AFA：[Journal of Finance submissions](https://afajof.org/submissions/)。分别核查代码、披露、费用；不外推其他金融刊。该页cover letter规则提醒勿默认所有刊都要通用投稿信。
- [Chartered ABS AJG](https://charteredabs.org/academic-journal-guide/academic-journal-guide-2024)：已核查官方入口，直接访问可能受限；个刊等级仍须查询。
- [ABDC Journal Quality List](https://abdc.edu.au/abdc-journal-quality-list/)：官方提供当前和历史列表，区分列表版年和发布年。
- [FT研究期刊名单](https://www.ft.com/content/db863a0a-6524-45f9-bc52-fee997634bdc)：名单有更新，不固定成员；短链接可能不可用。
- [UT Dallas journal list](https://jsom.utdallas.edu/the-utd-top-100-business-school-research-rankings/list-of-journals)：按指定研究名单核查，不称全领域完整榜。
- [IDEAS/RePEc](https://ideas.repec.org/top/top.journals.all.html)：运行时查时间和计量口径。
- [Clarivate MJL](https://mjl.clarivate.com/)、[JCR](https://clarivate.com/academia-government/scientific-and-academic-research/research-funding-analytics/journal-citation-reports/)、[SCImago](https://www.scimagojr.com/)、[中科院分区表](https://www.fenqubiao.com/)：入口不等于个刊当期数据已核实。
- [南京大学评价中心](https://cssrac.nju.edu.cn/gywm/zxjj/index.html)：已核查来源与扩展目录区分；个刊仍须正式目录核对。
- [北京大学图书馆](https://www.lib.pku.edu.cn/)：寻找正式核心目录版本，不用第三方标签代替。

除上述明确说明外，链接只作查询入口。不内置接受率、排名数值或费用；更新时重查来源状态、政策和版本，并重跑边界案例。
