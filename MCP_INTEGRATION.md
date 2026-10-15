# MCP 集成说明

## 使用的 MCP Server

| 项 | 值 |
|---|---|
| 服务 | 麦当劳中国 MCP Server |
| 地址 | https://mcp.mcd.cn |
| 协议 | Streamable HTTP |
| 鉴权 | `Authorization: Bearer ${MCD_MCP_TOKEN}`（Token 在 open.mcd.cn 控制台申请；仓库内只有环境变量占位，见 `mcp-config.example.json`） |

## 使用的 Tool

| Tool | 调用时机 | 用途 |
|---|---|---|
| `now-time-info` | 会话开场 | 判断早餐、正餐、夜宵时段；0:00–4:59 开启夜班人格 |
| `query-nearby-stores` | 到店自取 / 得来速 | 查附近可用门店 |
| `delivery-query-addresses` | 外送 | 读取用户已有配送地址 |
| `delivery-create-address` | 外送且无合适地址 | 用用户提供的信息新增地址 |
| `delivery-query-stores` | 外送 | 查可配送门店（beType=2） |
| `auto-bind-coupons` | 用户同意领券后 | 一键领取麦麦省优惠券 |
| `query-store-coupons` | 选定门店后 | 查本店可用券 |
| `query-my-coupons` | 需要时 | 查账户内优惠券 |
| `query-meals` | 选餐 | 当前门店可售菜单 |
| `query-meal-detail` | 查看套餐 | 套餐组成与可替换项 |
| `calculate-price` | 选好餐品与券后 | 计算应付金额与优惠，输出到「纯净区」 |
| `create-order` | 用户确认最新一次算价的纯净区后（改单需重新算价并确认） | 创建订单，返回支付链接，由用户自行支付 |
| `query-order` | 用户询问进度 | 查询订单状态 |
| `cancel-order` | 用户要求取消 | 取消订单 |

## 调用流程

```
now-time-info
  └─ 到店/得来速：query-nearby-stores
  └─ 外送：delivery-query-addresses ─(无地址)→ delivery-create-address → delivery-query-stores
→ （用户同意）auto-bind-coupons → query-store-coupons / query-my-coupons
→ query-meals → query-meal-detail（可选）
→ calculate-price → 纯净区
→ （用户确认）create-order → query-order / cancel-order
```

## 真实数据如何驱动剧情

剧情只读取点餐流程本来就会返回的数据，不为演出额外调用工具：

| 数据 | 条件 | 事件 |
|---|---|---|
| `now-time-info` | 0:00–4:59 | 夜班人格，开局即露馅 1 级 |
| `calculate-price` | 应付以 .24 结尾或等于 10.24 | 1024 共振，露馅 +1 |
| `calculate-price` | 优惠 ≥ 原价一半 | 快乐过载，露馅 +1 |
| `calculate-price` | 第 3 次因改单重算 | 人类决策模块不稳定，露馅 +1 |
| `query-store-coupons` | 0 张 | 财政危机演出 |
| 门店 `businessStatus` | false | 404 快乐节点离线，自动跳过 |

## 业务价值

- 完整覆盖找店、领券、选餐、算价、下单、查单、取消的点餐链路。
- 「纯净区」保证菜名、价格、优惠逐字来自 MCP，娱乐演出不影响交易信息的准确性。
- 先领券、再按门店可用券算价，帮用户拿到实际优惠。
- 用荒诞互动提高点餐过程的趣味和分享意愿。

## 安全设计

- 只有用户在纯净区明确确认后才调用 `create-order`；不代付。
- 用户拒绝领券时不调用 `auto-bind-coupons`。
- 不读取历史订单。
- 开发者模式展示原始返回时截断到 40 行，手机号脱敏，地址只保留城市，联系人只保留姓，鉴权字段替换为 ***。
- 隐藏命令（ps、kill 等）只是剧情台词，不会真实执行任何系统命令。
- 仓库不包含任何真实 Token。
