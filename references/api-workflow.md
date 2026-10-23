# EDA 执行与 API 适配

## 连接与变更范围

- 使用另行安装的 `easyeda-api` 和 EDA 专业版 `run-api-gateway`；只开启任务所需的外部交互能力。
- 对当前实际 checkout 检查 package.json 的 scripts，安装依赖并按支持的入口启动桥接；不盲跑过时 README 命令。
- 服务通常扫描本机 49620–49629。核对 `/health` 的 `service: easyeda-bridge`、连接状态和目标 EDA 窗口。
- 远程云会话的 localhost 不等于用户电脑；不探测无授权服务，不声称已连接用户本机。
- 读取当前项目及活动文档；SCH API 只在目标原理图上运行，PCB API 只在目标 PCB 上运行。
- 没有桥接时继续离线计划/文件审查，报告未应用。不要编造执行结果。
- 在可恢复副本/快照上先验证 beta API；不要把版本不兼容的调用直接全量应用。

## API 纪律

- 每个新 API 先读当前版本完整签名、参数单位、枚举、返回对象和示例，必要时探测一项。
- PCB 坐标通常 1 mil/单位：`mm / 0.0254`；原理图通常 10 mil/单位：`mm / 0.254`。
- 按具体属性核实单位，不假定所有距离、字体或规则接口共用画布单位。
- 大多数原理图 API 的 Y 增大向上，矩形高度向下延伸；读取现有对象核对方向和原点。
- `await` 所有异步调用。按当前 API 使用 `toAsync() → setState_*() → done()` 或 `modify()`。
- 优先使用已验证运行时枚举；缺少全局枚举时仅在已核实映射后用数值，不乱猜。
- 原理图导线可有 `.line`、`.net`，不要假定存在 `getState_Coordinates()`。
- 元件枚举可能包含网络标记/端口；用实际类型/位号筛选并核实，不把对象总数当器件数。
- 大段 JS/JSON 写入 UTF-8 临时文件再提交；用系统临时目录，兼容 Windows，避免 shell 字符串拼接。
- 小批执行并检查失败项；失败时读回现场再重试，避免部分成功后重复创建。
- 导出、ERC/DRC、规则读写方法以当前 API 为准；没有该方法时使用可用 UI 或明确列出待人工步骤。

## 器件值原生属性优先示例

以下调用来源于下载的 API 文档；使用前仍须核对当前运行时签名。
`compId`、`silkLayer`、`pos`、`fontSize`、`lineWidth` 必须从实际工程/单位换算得到。

```javascript
const attrs = await eda.pcb_PrimitiveAttribute.getAll(compId);
const valueAttr = attrs.find(a => a.getState_Key() === confirmedValueKey);
if (valueAttr) {
  await eda.pcb_PrimitiveAttribute.modify(valueAttr.getState_PrimitiveId(), {
    layer: silkLayer, x: pos.x, y: pos.y,
    keyVisible: false, valueVisible: true, fontSize, lineWidth
  });
  const check = await eda.pcb_PrimitiveAttribute.get(valueAttr.getState_PrimitiveId());
  // 按当前类型读取值、可见性、图层和位置，并和期望逐项比较。
}
```

- `confirmedValueKey` 从属性清单和来源确认，可能是 Value 或经核实的自定义键；不要拿器件描述代替值。
- 上述代码只设置显示参数，不改写电气属性值；需要短写时用额外显示属性/文本。
- 按当前签名，器件 `setAttribute(key, value, keyVisible, valueVisible)` 可创建关联属性，
  返回的属性图元再用 `pcb_PrimitiveAttribute.modify()` 放到正确丝印层和位置。
- 例如创建专用 `SilkValue` 属性时先确认键没有用户自定义用途；保留 Value/BOM 原值。
- 新增自定义显示属性后读取 PCB 网表，核实它是否进入与原理图的属性比对。
  若仅用于版面的属性造成同步差异，改用有持久归属记录的丝印文本；不要改电气网表或关闭比对来掩盖差异。
- 按当前 API 同样核对原生位号属性；用两条文本显示时分别重读，不能只检查值。
- 不适用时读取 `PCB_PrimitiveString` 当前 create/modify/get/delete 签名创建受管理文本。
  核实 layer、mirror、reverse 和父子关系；不要臆造 `showValue()` 一类接口。
- 需要替换/去重时只针对确认归属对象；保留用户位号、极性与其他手工丝印。
