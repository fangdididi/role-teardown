[English](README.md) | **简体中文**

# Role Teardown（岗位拆解）

> 像逆向工程师一样拆开招聘启事。用证据重建你的申请材料，其余的统统删掉。

大多数 AI 代写的求职材料长得一模一样：照抄职责清单，开头就是“热爱行业、学习能力强、抗压能力强”，把做过的每件事都列上，有时还会为了补缺口编出一项技能。HR 几秒钟扫一眼就翻过去了。

**Role Teardown** 是一个反过来做事的 agent 技能。它先解码用人团队真正需要什么（启事背后的问题，而不只是关键词清单），再把你的真实成就挖成可核实的**证据原子**，最后重建一份简短、具体的申请材料，让每一行都用证据回应启事。在你发出去之前，三种挑剔的读者（7 秒速读者、ATS 解析器、多疑的用人经理）会先审一遍。绝不编造：不知道的数字会变成醒目的 `[NEED NUMBER]` 占位，真正的缺口会被直说，而不是藏起来。

支持中文和英文，适用于各行各业：技术、产品、运营、市场、研究、设计。

```text
修改前  “参与 Listing 优化工作。”                       → 没有结果、没有数字、对不上要求
修改后  “用 ChatGPT、Claude 批量改写 220 条 Listing 标题和五点描述，按亚马逊 Listing
         规则沉淀 12 套提示词模板，主推款点击率 0.38% → 0.61%。” → 直接回应启事的核心职责
```

## 功能

- **五层拆解**任何招聘启事：明说、权重、隐含、门槛、噪音，每一行都标注是原文、推断还是猜测。
- **招聘假设**：用三句话说清这个岗位为什么存在、新人必须做成什么、团队最怕什么。后面的一切都指向它。
- **先查门槛**：如果某个硬性要求（年限、学历、地点、签证、语言）明显不满足，动笔之前就会告诉你。
- **证据原子**按是否带数字和凭据分为 A/B/C 三级；**匹配图**把每项要求标为覆盖、部分、缺口或门槛，并为每个缺口给出诚实的处理方式。
- **精简构建规则**：每一行都要交房租；简历前三分之一回应招聘假设；求职信三步走（他们的问题、我的凭据、头几步）。
- **三种读者的红队审阅**：速读者、解析器（ATS）、怀疑者，每人最多三条发现。
- **面试弹药**：30 秒自我介绍、五拍式证据故事、验证招聘假设的反问、缺口预演。
- **辅助脚本**（`scripts/teardown.py`，只用 Python 3 标准库）：从启事里提取加权要求词和硬门槛；计算简历的加权覆盖率并检查是否出现在前三分之一；检查套话、职责式条目、缺少数字和未填占位。中英文都支持。
- **内置诚信规则**：不编造事实、不藏关键词、推断内容有标注、不代你发送任何东西。

## 八轮流程

```text
 1 剥层      招聘启事 → 五层 + 门槛检查
 2 立假设    为什么是这个岗位、为什么是现在、他们怕什么
 3 探查      不超过 5 个公开来源（可选）
 4 挖证据    你的材料 → 证据原子（A/B/C）
 5 画匹配    要求 → 原子 → 覆盖 / 部分 / 缺口 / 门槛
 6 删减      精简简历 + 三步求职信
 7 定声音    具体名词、数字、去套话（lint）
 8 红队      速读者 · 解析器 · 怀疑者 → 修改 → 面试弹药
```

## 安装

技能就是这个文件夹本身，agent 读取的是 `SKILL.md`。文件夹请命名为 `role-teardown`。

**Claude Code**

```bash
# 对所有项目生效
git clone https://github.com/fangdididi/role-teardown ~/.claude/skills/role-teardown
# 或者只对当前项目生效
git clone https://github.com/fangdididi/role-teardown .claude/skills/role-teardown
```

**OpenAI Codex**

```bash
git clone https://github.com/fangdididi/role-teardown ~/.codex/skills/role-teardown
```

**Cursor**

```bash
git clone https://github.com/fangdididi/role-teardown .cursor/skills/role-teardown
```

**Gemini CLI、OpenCode、Windsurf 及其他 agent**

如果 agent 有技能目录（常见的是 `.agents/skills/`），克隆进去即可。使用开放的 skills 安装器的话，也可以运行 `npx skills add fangdididi/role-teardown`。如果你的 agent 没有技能系统，在 `AGENTS.md`、`CLAUDE.md` 或规则文件里加一行：

```text
当我发来招聘启事时，按照 ./role-teardown/SKILL.zh-CN.md 的方法工作，并使用其中的 scripts/teardown.py。
```

辅助脚本需要 Python 3.8 或更高版本。不用脚本，方法本身也能用。

## 使用

把招聘启事（或链接）和简历贴给 agent，用平常的话提要求：

```text
这是 JD 和我的简历，帮我拆一下，再改申请材料。
这个岗位适合我吗？先剥层、画匹配图，先不用写。
周五要面这个岗位，帮我准备弹药。
```

agent 会一次性问最多五个开场问题（专门挖你简历里藏着的证据），然后把拆解包写进 `applications/<公司>-<岗位>/`：

```text
teardown.md   五层、招聘假设、探查记录、证据原子、匹配图、删减清单
cv.md         定制简历
note.md       求职信或申请留言
review.md     红队发现、覆盖率和 lint 的修改前 → 修改后
interview.md  自我介绍、证据故事、反问、缺口预演
```

也可以单独运行脚本：

```bash
python3 scripts/teardown.py signals  examples/zh-ai-product-ops/posting.md
python3 scripts/teardown.py coverage examples/zh-ai-product-ops/posting.md examples/zh-ai-product-ops/cv.md
python3 scripts/teardown.py lint     examples/zh-ai-product-ops/cv.md
```

## 示例

对中文示例启事运行 `signals`（节选）：

```text
TITLE: AI 产品运营（跨境卖家工具方向）（虚构示例）

REQUIREMENT SIGNALS (higher = stated harder, earlier, more often)
 score   n  term  [sections]
   6.2   3  Listing  [duty, must, noise]
   6.0   2  亚马逊  [duty, must]
   5.4   2  提示词  [duty, must]
   3.9   1  电商运营  [must]

HARD GATES (check these before writing anything)
  - location: 云帆出海 · 深圳南山 · 全职 · 每周 1 天可远程
  - experience: 本科及以上学历，3 年以上互联网产品运营或电商运营经验。
  - degree: 本科及以上学历，3 年以上互联网产品运营或电商运营经验。
  - language: 英语读写流畅，能看懂英文平台政策。
```

对原始简历运行 `lint`（节选）：

```text
GENERIC (6)
  - 热爱
  - 积极主动
  - 抗压能力强
  - 学习能力强
  - 团队合作精神
  - 认真负责

DUTY-NOT-RESULT (3)
  - L10: 负责 3 个店铺的日常运营。
  - L11: 参与 Listing 优化工作。
  - L14: 协助客服处理差评。
```

| 示例 | 语言 | 岗位 | 覆盖率 | lint 问题 |
|---|---|---|---|---|
| `examples/en-data-engineer/` | 英文 | 虚构包裹物流公司的高级数据工程师 | 44% → 94% | 12 → 0 |
| `examples/zh-ai-product-ops/` | 中文 | 虚构跨境卖家工具公司的 AI 产品运营 | 40% → 83% | 12 → 0 |

每个示例文件夹都包含招聘启事、原始简历、完整的 `kit.md`（八轮全部走完）、定制简历和求职信。示例中的公司和人物均为虚构。

## 文件结构

```text
role-teardown/
├── SKILL.md                         # 技能本体（英文），agent 读取
├── SKILL.zh-CN.md                   # 技能本体（中文）
├── README.md                        # 英文说明
├── README.zh-CN.md                  # 本文件
├── LICENSE                          # MIT
├── scripts/
│   └── teardown.py                  # signals / coverage / lint
├── templates/
│   ├── teardown-kit.md              # 空白拆解包骨架（英文）
│   └── teardown-kit.zh-CN.md        # 空白拆解包骨架（中文）
└── examples/
    ├── en-data-engineer/
    │   ├── posting.md  cv.md  kit.md  cv.tailored.md  note.md
    └── zh-ai-product-ops/
        ├── posting.md  cv.md  kit.md  cv.tailored.md  note.md
```

## 它不会做的事

- 编造经历、数字、工具或证书。
- 隐藏或堆砌关键词。
- 替你提交申请、给招聘方发邮件或私信任何人。
- 把你的简历上传到任何地方。

覆盖率高只说明你的措辞和启事对得上，并不能让一个说法变成真的。所以这个技能永远把一条 A 级证据原子看得比一个关键词更重。

## 许可证

[MIT](LICENSE) © 2026 fangdididi
