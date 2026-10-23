# jlc-easyeda-design

给 AI Agent 用的嘉立创 EDA 专业版设计 Skill，把原理图、电气审核、PCB 布局布线、GND 铺铜、器件值丝印和交付检查放进同一套流程。

**当前版本：1.0.3** · **MIT License**

## 原理图示例

[![原理图整理效果示例](https://raw.githubusercontent.com/Ibook000/jlc-easyeda-design/main/assets/examples/schematic-keyboard.png)](https://github.com/Ibook000/jlc-easyeda-design/blob/main/assets/examples/schematic-keyboard.png)

原理图整理效果示例，点击图片查看原图。

## 能做什么

| 任务 | 关注点 |
| --- | --- |
| 原理图设计与整理 | 器件引脚映射、模块分区、实际连线、跨模块网络标签、图纸拆分 |
| 电气与连接审核 | 电压域、供电、去耦、启动配置、接口、网表一致性和 ERC |
| PCB 布局布线 | 机械约束、关键器件布局、电源回路、差分与高速信号、连续回流路径 |
| 设计规则 | 线宽、间距、过孔、板边铜和网络类，写入项目后重新读取核对 |
| GND 铺铜 | 网络绑定、孤岛、窄颈、断地和跨缝回流检查 |
| 器件值丝印 | 保留位号，显示实际值，如 `R1 10k`、`C3 100nF`、`L1 4.7uH` |
| 修改后验收 | 按修改范围检查 ERC、DRC、未连接网络、铺铜和实际导出的丝印 Gerber |

模块内部优先使用清楚的实际连线，跨模块按需要使用网络标签。密集器件可以做引脚扇出；图纸放不下时可以拆页或扩大图纸。

## 依赖与运行方式

- 使用支持 `SKILL.md` 的 AI Agent。
- 在线读写工程需要嘉立创 EDA 专业版、[easyeda-api](https://github.com/easyeda/easyeda-api-skill) 和 [run-api-gateway 插件](https://jlcext.com/item/oshwhub-official/run-api-gateway)。按依赖说明连接桥接服务，并确认当前工程和文档。
- 附带的丝印清单脚本使用 Python 3 标准库，无需安装第三方 Python 包。建议使用 Python 3.10 或更高版本。

本 Skill 提供设计流程和检查规则，实际 EDA 操作由 `easyeda-api` 执行。没有桥接连接时，可以做离线审查和修改方案，工程不会因此自动改变。自动布线能力取决于实际连接的工具，本仓库不提供布线求解器。

## 安装

下面将仓库安装到本机使用的 `~/.agents/skills/` 目录。其他 Agent 请改成对应的技能目录。

**Windows PowerShell：**

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills" | Out-Null
git clone https://github.com/Ibook000/jlc-easyeda-design.git "$env:USERPROFILE\.agents\skills\jlc-easyeda-design"
```

**macOS / Linux：**

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/Ibook000/jlc-easyeda-design.git "$HOME/.agents/skills/jlc-easyeda-design"
```

也可以下载仓库 ZIP，解压后将含有 `SKILL.md` 的整个目录放进技能目录，并命名为 `jlc-easyeda-design`。

安装后让 Agent 重新加载技能，或开启新会话。确认技能列表中出现 `jlc-easyeda-design`。依赖 `easyeda-api` 需要另行安装。

如果此前安装了 `easyeda-schematic-net-fanout`，并准备使用本 Skill 替代它，可以将旧技能移到技能目录外备份，避免重复触发。保留 `easyeda-api`。

## 使用示例

显式指定 `$jlc-easyeda-design`，再描述工程、目标和需要保留的部分。

**审核原理图：**

```text
使用 $jlc-easyeda-design 审核当前原理图，检查供电、去耦、启动配置和接口引脚。
先读取实际器件与连接，列出有证据的问题；暂不修改工程。
```

**布局布线与铺铜：**

```text
使用 $jlc-easyeda-design 整理当前 PCB。
保持板框、安装孔和接口位置，先核对电源电流、叠层与关键网络约束，
再调整布局和布线、重建 GND 铺铜，写入并读回设计规则。
完成后报告实际执行的检查和剩余问题。
```

布局整理优先利用已经确认有空间的模块下方，核对器件高度与装配间隙；从焊盘中心出线，
转角优先 45°，清除栅格布线留下的小台阶、重复并线和多余泪滴。
GND 主要依靠连续铺铜，重建后逐个检查地焊盘与过孔是否真正连通。
具体做法见 [布局与线形整理](references/pcb-layout-refinement.md)。

整理后还会检查不同路径拼接处的转角、密集地焊盘的接入空间，并按实际 Gerber 核对每组丝印。
覆盖区外的成组标注保持对齐与明确对应，制造尺寸检查和版面可读性分别验收。

**只补器件值丝印：**

```text
使用 $jlc-easyeda-design 给当前 PCB 的电阻、电容、电感补充实际值丝印。
保留位号与铜层设计，按当前装配版本核对数值，区分顶底面，避免重复标签。
无法放下的器件单独列出，不要静默隐藏。
```

## 丝印清单脚本

脚本从规范化的器件清单生成期望文本，并核对从 EDA 重新读取的标签。它不连接 EDA，也不负责放置文字或检查几何重叠。

在仓库根目录运行：

```bash
python scripts/silkscreen_values.py plan examples/inventory.json --out plan.json
```

示例会生成 `R1 10k`、`C3 100nF` 和 `R8 DNP`。`examples/inventory.json` 是演示数据；实际使用时，应从目标工程和装配版本构建自己的清单，并核实数值来源。

通过 EDA 工具应用标签后，重新读取实际文本、层、可见性及图元 ID，再运行：

```bash
python scripts/silkscreen_values.py audit inventory.json readback.json --out audit.json
```

`inventory.json` 和 `readback.json` 的完整格式见 [silkscreen-data.md](references/silkscreen-data.md)。不要把 `plan.json` 复制成实际读回数据。

| 结果 | 含义 |
| --- | --- |
| `planned` | 文本计划已生成，尚未修改 EDA |
| `passed` | 本次清单的文本、层、可见性和覆盖核对通过 |
| `failed` | 存在缺值、遗漏、旧值、错误层、隐藏、重复或孤立标签等问题 |
| `not_applicable` | 输入范围没有适用的标签，且未发现清单问题 |

命令退出码：`0` 为成功或不适用，`1` 为清单检查发现问题，`2` 为输入或文件错误。清单核对通过后，仍需检查文字尺寸、间距、底面阅读效果和实际导出的丝印 Gerber。

## 规则与验证

执行流程为：读取工程与约束 → 保存可恢复快照 → 小批修改 → 重新读取核对 → 按范围验收。

默认参数集中在 [defaults.json](references/defaults.json)。其中普通信号线宽、间距均为 `0.20 mm`，过孔外径/钻孔为 `0.60/0.30 mm`，用于普通低压 FR-4、1 oz 板的候选起点。使用前应核实器件、实际制造选项和工程约束；电源线宽、差分阻抗等仍需按实际条件计算。

API 返回成功后还要读回核对。ERC、DRC、Gerber 或制造检查未执行时应明确记录；只调整丝印时，验收范围也应对应丝印和本次变更。

## 目录

```text
jlc-easyeda-design/
├── SKILL.md                         # 技能入口与统一流程
├── agents/openai.yaml               # 技能展示与调用配置
├── assets/
│   ├── icon.svg                     # 技能图标
│   └── examples/schematic-keyboard.png # 原理图展示示例
├── examples/inventory.json          # 可运行的演示器件清单
├── references/
│   ├── api-workflow.md              # 桥接连接与 API 适配
│   ├── schematic-rules.md           # 原理图与电气审核
│   ├── pcb-rules.md                 # PCB 布局、布线与铺铜
│   ├── pcb-layout-refinement.md     # 模块下方利用、45° 转角与线形整理
│   ├── silkscreen-rules.md          # 器件值丝印规则
│   ├── silkscreen-data.md           # 脚本输入输出格式
│   ├── verification.md              # 验收与交付检查
│   ├── defaults.json                # 候选默认参数
│   └── sources.md                   # 来源、版本与适用范围
├── scripts/silkscreen_values.py     # 丝印文本计划与读回核对
└── LICENSE
```

## 来源与许可

本项目整合并改写了 [jlc-easyeda-pcb-routing](https://github.com/LJ951/jlc-easyeda-pcb-routing) 和 [easyeda-enhanced-schematic-skill](https://github.com/easyeda/easyeda-enhanced-schematic-skill) 的相关工作流程，使用 [easyeda-api-skill](https://github.com/easyeda/easyeda-api-skill) 作为外部执行依赖。具体来源版本与适用范围见 [sources.md](references/sources.md)。

采用 [MIT License](LICENSE)，保留上游版权声明。
