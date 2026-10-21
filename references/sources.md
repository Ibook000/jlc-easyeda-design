# 来源与适用范围

整合并改写以下下载版本的工作流程；保留来源，避免将经验默认值声称为制造保证。

| 来源 | 下载版本/用途 |
| --- | --- |
| https://github.com/LJ951/jlc-easyeda-pcb-routing | `7ba193bd087f1a789f3f6aa1623b98387c4f3fb5`；布局、GND、布线、制造验收；MIT，版权声明见 LICENSE |
| https://github.com/easyeda/easyeda-enhanced-schematic-skill | `0c4b9a0ad94d532923dee5c828a6efa7444f4506`；元件分区、引脚扇出及 API 注意事项；上游 frontmatter 声明 MIT |
| https://github.com/easyeda/easyeda-api-skill | 外部执行依赖；用当前安装版本的签名、类型、桥接说明，不复制整套 API 包 |

新增内容包括电气/网表审核、局部修改范围、参数写入读回、完整器件值丝印策略、
幂等更新及覆盖审计；保留 EDA/制造验证的实际能力边界。

使用时按需要查当前权威资料：

- 嘉立创 EDA 专业版设计规则：https://prodocs.lceda.cn/cn/pcb/design-design-rule/index.html
- EasyEDA Pro 铜区：https://prodocs.easyeda.com/en/pcb/place-copper-region/index.html
- JLCPCB 当前工艺能力：https://jlcpcb.com/capabilities/pcb-capabilities
- 网关插件：https://jlcext.com/item/oshwhub-official/run-api-gateway
- TI 高速布局指南：https://www.ti.com/lit/an/scaa082a/scaa082a.pdf
- 对应芯片、接口、模块和连接器官方 datasheet/reference layout。

核实页面版本与实际下单选项；不要将上游未获取正文的外部文章当作已验证规则。
