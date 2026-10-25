这 22 道抽检题目的**主时间窗口边界、参考 SQL 过滤条件、干扰项注入探针（Distractor Probe）以及 `generate_series` 日期骨架全部对得上**，与词典（Glossary）定义的口径 100% 一致。

不过在底层的 **Sensitivity Evidence（$\pm 1$ 天敏感性校验）** 中，有 **1 道题（`v4_246`）发现了哈希碰撞/伪阳性漏洞**，另外在抽样覆盖度上有一个小隐患。以下是逐项核对结果与 Manual Worksheet 填表参考：

---

### 1. 核心时间窗口核对表（可直接用于填写 Manual Worksheet）

词典基准：`reference_date = 2026-10-22`（UTC），半开区间 `[start, end)`，而 `generate_series(start, stop, '1 day')` 在 DuckDB 中为**双闭区间**，因此其结束参数应为 `Inclusive final date`（即 `Exclusive end - 1 day`）。代码中这一点处理得非常准确。

| 题目编号 | 题面时间表述 | Inclusive start | Inclusive final date (`generate_series` 终点) | Exclusive end (`&lt; TIMESTAMP` 边界) | `Code-computed` &amp; `Probe` | 核对结果 |
| --- | --- | --- | --- | --- | --- | --- |
| **v4_001, v4_006, v4_061, v4_066, v4_121, v4_126** | `For the last 7 days` | `2026-10-15` (`00:00:00Z`) | `2026-10-21` | `2026-10-22` (`00:00:00Z`) | `['2026-10-15', '2026-10-22']` | **完全一致** |
| **v4_181, v4_196, v4_211, v4_226** | `For the last 7 days` (含 `generate_series`) | `2026-10-15` | `2026-10-21` (`generate_series` 终点为 `10-21`) | `2026-10-22` (`WHERE &lt; '10-22'`) | `['2026-10-15', '2026-10-22']` | **完全一致** |
| **v4_241, v4_256** | `For the last 7 days` (无 `generate_series`) | `2026-10-15` | `2026-10-21` | `2026-10-22` | `['2026-10-15', '2026-10-22']` | **完全一致** |
| **v4_186, v4_201, v4_216, v4_231** | `For previous week` (含 `generate_series`) | `2026-10-08` | `2026-10-14` (`generate_series` 终点为 `10-14`) | `2026-10-15` (`WHERE &lt; '10-15'`) | `['2026-10-08', '2026-10-15']` | **完全一致** |
| **v4_246, v4_261** | `For previous week` (无 `generate_series`) | `2026-10-08` | `2026-10-14` | `2026-10-15` | `['2026-10-08', '2026-10-15']` | **完全一致** |
| **v4_271, v4_276, v4_286, v4_291** | 对照层 (无时间窗口) | `N/A` | `N/A` | `N/A` | `None` / `triggered: false` | **完全一致** (未误触发 2017 干扰项) |

---

### 2. 发现的 3 个潜在问题（建议在 Commit 冻结前检查）

#### 问题 A：`v4_246` 的 $\pm 1$ 天敏感性校验存在“左移 = 右移”哈希完全一致的异常

看 `v4_246`（`rustdesk/rustdesk` 在 `previous week [10-08, 10-15)` 的 `PushEvent` session_count）：

* `shift_days: -1`（`[10-07, 10-14)`）的 `rows_sha256` 是：`77471ebe3613f4714666523fa961eb443f57dc2396a31528afdbbea86fadc8f8`
* `shift_days: +1`（`[10-09, 10-16)`）的 `rows_sha256` **也是**：`77471ebe3613f4714666523fa961eb443f57dc2396a31528afdbbea86fadc8f8`

**为什么这很危险：**

1. **越界空数据：** 你的快照时间范围是 **2026-10-08 至 10-21**。当 `previous week`（起点就是 `10-08`）做 `shift_days: -1` 变成 `[10-07, 10-14)` 时，**`2026-10-07` 在数据库里根本没有数据**！同样，当 `last 7 days`（终点是 `10-22`）做 `shift_days: +1` 变成 `[10-16, 10-23)` 时，**`2026-10-22` 在数据库里也根本没有数据**！
2. 在 `v4_246` 中，`[10-07, 10-14)` 实际上只查了 `[10-08, 10-14)`（6 天），而 `[10-09, 10-16)` 查了 7 天，两者算出来的单行标量 `session_count` 碰巧完全相等（哈希一模一样），只比基准 `[10-08, 10-15)` 少（或多）了刚好相等的值。
3. 对于返回单行单列标量（`row_count: 1`）的题目，如果 Agent 写错了一个窗口边界（比如把 `&gt;= 10-08 AND &lt; 10-15` 写成了 `&gt;= 10-08 AND &lt;= 10-15` 或偏移了窗口），极易因为标量数值巧合相等而产生碰撞。

#### 问题 B：抽检的 22 道题只覆盖了 2 种时间短语（`last 7 days` 和 `previous week`）

* 这 18 道带时间窗口的抽检题中，所有的 `literal` 题（共 9 道）全都是 **`For the last 7 days`** (`['2026-10-15', '2026-10-22']`)；
* 所有的 `distractor` 题（后 6 道）全都是 **`For previous week`** (`['2026-10-08', '2026-10-15']`)，前 3 道 `distractor` 题也是 **`For the last 7 days`**。
* 也就是说，你方案里设计的其他高风险窗口类型——**`last N days` ($N \in \{3, 5, 10, 14\}$)、`last week`、显式闭区间（`"October X through October Y"`，最容易犯 inclusive end 不加 1 天的错）、以及 `since &lt;date&gt;**`——在这 22 道抽检题里**一道都没有出现**！
* **原因分析：** 很可能是因为你的抽样脚本按固定题号步长（例如 `001, 006, 061, 066...` 每隔 5 题/15 题取一道）抽样，而生成器在遍历笛卡尔积时的内层循环周期刚好与抽样步长发生了**模数共振（Modulo Resonance / Aliasing）**，导致抽出来的全都是同一个窗口槽位！
* **强烈建议：** 抽检的 20~22 道题如果在时间短语维度上没有覆盖 `explicit range (through)`、`since` 和 `last week`，人工质检就漏掉了最容易写错边界转换逻辑的生成器分支。建议立刻手动挑几道包含 `"through"` 和 `"since"` 的题目看一眼它们的 `Code-computed boundaries`。

#### 问题 C：`events` 表与 `repos` 表的冗余 `JOIN` 不一致

* 在前 6 道窗口题（`v4_001` 到 `v4_126`）中，即使 `WHERE` 条件只过滤了 `e.repo_name = '...'`（完全没用到 `r.language` 等 `repos` 表字段），参考 SQL 依然写了 `FROM events e JOIN repos r ON r.repo_id = e.repo_id`。
* 而在后面的高级 SQL 题（`v4_181` 到 `v4_261`）中，同样是按 `e.repo_name` 过滤，参考 SQL 却**没有** `JOIN repos r`。
* **隐患：** 如果 `events` 表中存在孤儿事件（即某个 `repo_id` 不在 catalog `repos` 表中），`INNER JOIN repos` 会过滤掉这些事件，而不 `JOIN` 则会保留。虽然抽检的这几个知名仓库肯定在 `repos` 表里，但最好确认快照构建时 `events.repo_id` 是 `repos.repo_id` 的严格子集（外键完整）。

---

### 总结结论

1. **当前这 22 道题本身：** 时间窗口计算、半开区间 `&lt; end`、以及 `generate_series` 的闭区间终点 `-1 day` **100% 正确**，可以直接签字通过（Pass）。
2. **下一步动作：** 请务必在题集中额外扫一眼包含 **`"through"`（显式双闭日期区间）** 和 **`"since"`** 的生成题（因为当前抽样由于步长共振全部落在了 `last 7 days` 和 `previous week` 上），确认这两类模板的边界计算也同样准确。
