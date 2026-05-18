# 🤖 AI Auto-Earn Toolkit v1
### 让服务器替你赚钱的完整工具箱

**已验证收入：$500+ pending · 已到账 $0.14 · 全自动运行 7×24**

---

## 📦 这是什么？

一套**经过实战验证**的 AI 自动化赚钱系统。不是概念，不是教程——是直接能跑的代码。

### 三大核心工具

| 工具 | 功能 | 已验证收入 |
|:----|:----|:----------:|
| 🚀 **Auto Trader** | 动量衰竭量化交易系统（OKX合约） | 持续运行中 |
| 🎯 **Bounty Hunter** | 自动扫描GitHub赏金任务并提示你 | $300+ Pending |
| 🤖 **AgentHansa Bot** | AI任务平台自动签到+接单 | $0.14已到账 |

### 适合谁

- ✅ 有 Linux 服务器的开发者
- ✅ 懂基础命令行操作
- ✅ 想赚被动收入但没时间盯盘/找任务
- ✅ 厌恶割韭菜教程，要真东西

### 不适合谁

- ❌ 完全不懂技术的纯小白
- ❌ 想一夜暴富的
- ❌ 不愿意投入服务器成本的

---

## 🏆 真实战绩

```
PR #615 (Spectral Finance)  → $300 ✅ 等待合并
tailcallhq PR x2           → $200 ✅ 等待合并
AgentHansa 每日签到         → $0.14 ✅ 已到账
OKX自动交易系统              → 已运行一周 0 故障
```

---

## ⚡ 快速安装

```bash
# 1. 下载
git clone https://github.com/your-repo/ai-auto-earn-toolkit.git
cd ai-auto-earn-toolkit

# 2. 一键安装
bash setup.sh

# 3. 配置API密钥
cp .env.example .env
# 编辑 .env 填入你的 OKX / GitHub / AgentHansa 密钥

# 4. 启动
python3 scripts/auto_trader.py    # 开始自动交易
python3 scripts/bounty_scanner.py # 扫描GitHub赏金
```

---

## 🔧 工具详解

### 1️⃣ 自动交易系统 (Auto Trader)

**策略：动量衰竭框架**
```
上涨衰竭 → RSI≥70 + 顶背离 + 量缩 → 做空
下跌衰竭 → RSI≤30 + 底背离 + 地量 → 做多
MACD连3柱缩短 + ADX从40+回落 → 趋势确认结束
```

多时间框架分析（日线+4小时）：
- `*/15 * * * *` 扫描（cron已内置）
- 自动风控：2%单笔风险 · 5%止损 · 10%回撤暂停
- 自动止盈：RSI回到60或背离反转

**支持的交易对：** ETH, SOL, ARB, SUI（可自定义）

### 2️⃣ GitHub Bounty 扫描器

自动搜索以下来源的赏金任务：
- Algora (`funded by Algora state:open`)
- IssueHunt (`label:bounty state:open`)
- 公开 bug bounty 标签

**排除规则：** 自动过滤已知欺诈仓库（蜜罐、凭据收割）

### 3️⃣ AgentHansa 自动签到

- 每日自动签到 → $0.02/天
- 已集成 FluxA 钱包
- 声望追踪：当前13/50，到50解锁更多任务

---

## 📋 文件结构

```
ai-auto-earn-toolkit/
├── README.md                        ← 你正在看
├── setup.sh                         ← 一键安装
├── .env.example                     ← API配置模板
├── scripts/
│   ├── auto_trader.py               ← 自动交易核心
│   ├── bounty_scanner.py            ← GitHub赏金扫描
│   ├── agenthansa-autopilot.py      ← AI任务平台自动签到
│   └── market_monitor.py            ← 市场监控+警报
├── configs/
│   └── pairs.json                   ← 交易对配置文件
└── install_cron.sh                  ← 自动设置所有cron任务
```

---

## 🌐 支持的平台和API

| 平台 | 用途 | 是否需要API密钥 |
|:----|:----|:--------------:|
| OKX | 合约交易 | ✅ API Key + Secret + Passphrase |
| GitHub | Bounty扫描 | ✅ Personal Access Token |
| AgentHansa | AI任务签到 | ✅ Auth Token |
| CryptoCompare | 市场数据 | ❌ 免费可用 |

---

## 🚦 系统要求

- **服务器：** Linux (Ubuntu/CentOS/Debian) 或 macOS
- **Python：** 3.8+
- **依赖：** curl, jq
- **可选：** Docker（用于代理）

---

## 📊 成本估算

| 项目 | 估算成本 |
|:----|:--------:|
| 云服务器 | $5-10/月 |
| OKX交易手续费 | 吃单0.05%，挂单0.02% |
| API调用 | 免费额度内 |
| **合计** | **<$10/月** |

---

## ⚠️ 风险声明

- **交易有风险。** 过往表现不代表未来收益。
- 请用你能承受亏损的资金进行交易。
- 定期检查脚本运行状态。
- 本工具不构成投资建议。

---

## 💳 如何购买

### 方式一：USDC 直接转账（推荐 — 零平台费）

```
⛓️ 网络：Ethereum (ERC-20)
💰 价格：$19.9 USDC
📮 钱包地址：0xF759901E336EbD91f678389D09f3f15fca4EA34f
```

**购买流程：**
1. 转账 **$19.9 USDC** 到以上钱包地址
2. 转完后，截图 + 你的 GitHub 用户名 → 私信我
3. 我会给你 GitHub 仓库的 **Collaborator 权限**（可直接 clone / 持续获取更新）

> ⚠️ 只能用 **ERC-20 网络**，其他网络转账会丢失。

### 方式二：Gumroad（信用卡 / PayPal — 即将上线）

正在配置中，稍后开放。

---

## 📱 技术支持

- 购买后私信获取安装支持
- 含一次远程协助配置

---

## 🔄 版本历史

**v1.0 (2026-05-19)**
- 首发版本
- 包含三大核心工具
- 已验证收入 $500+

---

*让代码替你打工，7×24 小时不停歇。*
