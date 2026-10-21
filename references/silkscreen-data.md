# 丝印清单脚本

使用 Python 3 标准库。脚本只生成文本清单及核对实际读回的规范化标签，不控制 EDA。

```bash
python scripts/silkscreen_values.py plan inventory.json --out plan.json
python scripts/silkscreen_values.py audit inventory.json readback.json --out audit.json
```

退出码：0 表示该命令范围内成功/不适用，1 表示清单存在问题，2 表示输入或文件错误。
`planned` 只表示文本计划生成；`passed` 只表示清单核对通过，都不表示完成布板或制造检查。

## inventory.json

从当前目标工程及实际装配版本读取，按任务范围构建。不能仅收集已有标签的器件，
否则未标注的器件会从期望清单消失。

```json
{
  "components": [
    {"id":"pcb-r1","designator":"R1","kind":"R","value":"10k","side":"top","populated":true,"value_source":"当前装配版本 BOM R1，已与原理图核对"},
    {"id":"pcb-c3","designator":"C3","kind":"C","value":"100nF","side":"bottom","populated":true,"value_source":"当前装配版本 BOM C3"},
    {"id":"pcb-r8","designator":"R8","kind":"R","value":"","side":"top","populated":false,"value_source":"当前装配版本 DNP"}
  ]
}
```

- `id` 使用 PCB 稳定图元 ID；位号不可作为唯一的跨 ECO 关联依据。
- kind 使用 `R C L FB Y U Q D LED J SW F BT OTHER MECHANICAL`。
- 电气器件必须明确 `side`、JSON 布尔 `populated`、`value` 和 `value_source`。
- value 是核实的实际值、短型号或接口功能；不要拿封装名、料号或占位符替代数值。
- 纯数字无单位的无源值不能猜；例如 `value:"100",unit:"nF"`，不要只写 `100`。
- 原始 value 已含单位时 unit 留空；脚本仅拼接，不计算等值、不解码贴片字符、不校正来源。
- 保留大小写与小数，只把微符号和欧姆符号替换为 ASCII。`10mOhm` 与 `10MOhm` 始终不同。
- unknown DNP 可用空 value 加 `populated:false`；脚本标 DNP 并给警告，不推测名义值。
- MECHANICAL 仅适用已核实纯机械对象；脚本会拒绝把常见无源位号伪装成机械对象。
- 当前装配版本、器件属性或数据源冲突必须由调用者解决；脚本不证明数据本身正确。

## readback.json

应用变更后从 EDA 重新读取。只收集范围内可确认归属的值标签，以及本 Skill 管理的孤立标签。
普通板名、极性或用户注释不要混入值标签清单。

```json
{
  "labels": [
    {"component_id":"pcb-r1","designator":"R1","text":"R1 10k","layer":"top_silkscreen","visible":true,"text_ids":["r1-des-attr","r1-val-attr"]},
    {"component_id":"pcb-c3","designator":"C3","text":"C3 100nF","layer":"bottom_silkscreen","visible":true,"text_ids":["c3-combined-text"]},
    {"component_id":"pcb-r8","designator":"R8","text":"R8 DNP","layer":"top_silkscreen","visible":true,"text_ids":["r8-combined-text"]}
  ]
}
```

- 每个器件一个逻辑标签记录；位号和值分开显示时从实际文本按位号→值顺序合并，text_ids 列出两者。
- 只有该记录所有文本都可见且处于同一正确丝印层时，才能规范化为 visible:true 与该 layer。
- 一器件出现两套值文本时导出两条记录，审计会报告重复；不要在导出时先去重掩盖问题。
- layer 使用读取实际层定义后映射的 `top_silkscreen` 或 `bottom_silkscreen`；其他层不映射为丝印。
- 先核实 primitive ID 与器件关联，不凭文本最近距离认领归属。
- 多器件同面序号表需要拆成有独立图元 ID 的逻辑记录，避免共享 ID 被误判为完整覆盖。
- 不将 plan.json 复制成 readback.json，不自己填写未读取的可见性和 primitive ID。

脚本可发现空值、重复位号/ID、遗漏、旧值、错误侧面、隐藏、重复值标签及孤立关联。
之后仍须执行几何、制造尺寸、底面阅读及实际丝印 Gerber 检查。
