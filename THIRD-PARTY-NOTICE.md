# 第三方数据与许可

本仓库的 `data/journal-venues.json` 含派生自第三方开源项目的数据。按 MIT 许可要求，在此保留原始版权声明与许可全文。

## 派生数据

- 上游项目：Awesome-Journal-Skills（https://github.com/brycewang-stanford/Awesome-Journal-Skills）
- 上游文件：`catalog.json`
- 使用范围：仅提取金融、经济、会计、管理、公共政策相关条目的刊名、学科、地区、上游指示性分档与标签，用于召回与去重
- 未使用：上游的期刊策略正文、投稿建议与模板
- 获取日期：2026-11-20
- 上游自身声明：其 `tier` 字段为指示性分档，不构成排名或计量结论；费用、录用率、审稿周期、页数限制等易变事实不在该文件中

另 12 条中文刊条目由本仓库手写维护，只含刊名与学科归属。

## MIT License（上游）

```
MIT License

Copyright (c) 2026 Bryce Wang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 引用与二手使用

若你再分发本仓库的数据文件，请保留本节与上述许可文本。刊名与学科归属本身属于事实信息，但派生数据集的编排与字段选择沿用上游结构，应按 MIT 处理。
