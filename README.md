# 华巡网络设备巡检系统(Huaxuncheck)

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Netmiko](https://img.shields.io/badge/netmiko-4.1.2-blue.svg)](https://github.com/ktbyers/netmiko)

初衷就是为了更好的工作
一个简单易用的网络设备自动化巡检工具，支持多种网络设备（华为、H3C、锐捷、思科等）。

# 免责声明

- 这个项目免费开源，不存在收费。
- 本工具仅供学习和技术研究使用，不得用于任何商业或非法行为。
- 本工具的作者不对本工具的安全性、完整性、可靠性、有效性、正确性或适用性做任何明示或暗示的保证，也不对本工具的使用或滥用造成的任何直接或间接的损失、责任、索赔、要求或诉讼承担任何责任。
- 本工具的作者保留随时修改、更新、删除或终止本工具的权利，无需事先通知或承担任何义务。
- 本工具的使用者应遵守相关法律法规，尊重版权和隐私，不得从事任何违法或不道德的行为。
- 本工具的使用者在下载、安装、运行或使用本工具时，即表示已阅读并同意本免责声明。如有异议，请立即停止使用本工具，并删除所有相关文件。

# 公告

## 项目还在开发中，作者是编程老白菜，有些commit有bug，目前仅支持Windows 10，其他没条件没测试

## 功能特点

- 🚀 支持多种网络设备类型（Huawei、H3C、Ruijie、Cisco等）
- 🔄 自动执行预设命令获取设备状态和配置
- 📊 设备分组管理
- 📝 巡检结果记录和导出
- 📱 简洁直观的Web界面
- 🔒 支持SSH和Telnet连接
- 📦 支持设备信息批量导入/导出

## 快速开始

将代码pull到本地，直接运行start.bat，正常会弹出网页，开始愉快的摸鱼

### 环境要求

- Python 3.6+
- 依赖包（见requirements.txt）

### 🪟 Windows 部署步骤

1. 克隆项目
```
git clone https://github.com/2lodoss/Huaxuncheck.git

小白：直接 Github Download ZIP
```

2. 进入项目目录
```
cd Huaxuncheck

```

3. 启动系统
```
start.bat
注意：脚本默认每次执行清空数据库，请成功运行一次后，把脚本的清除数据库和安装依赖的命令注释掉。
```

4. 访问系统
打开浏览器访问：http://localhost:5000
如果提示端口被占用，请自行去程序中修改端口

## 使用说明

### 添加设备
1. 点击"添加设备"按钮
2. 填写设备信息（IP、用户名、密码等）
3. 选择设备类型和连接协议
4. 设置巡检命令
5. 点击"确定"保存

### 执行巡检
1. 选择要巡检的设备
2. 点击"执行巡检"按钮
3. 等待巡检完成
4. 查看巡检结果

### 分组管理
1. 点击"管理分组"按钮
2. 添加、编辑或删除分组
3. 将设备分配到相应分组

## 已成功支持的设备类型

- Huawei VRP
- H3C Comware
- Ruijie OS

## 项目结构

```
Huaxuncheck/
├── app.py                 # 后端主程序
├── requirements.txt       # 依赖包列表
├── start.bat             # Windows启动脚本
├── frontend/             # 前端文件
│   └── index.html        # 前端页面
└── network_inspection.db  # 数据库文件
```

## 贡献指南

欢迎提交Issue和Pull Request！在提交之前，请确保：

1. 代码符合PEP 8规范
2. 添加必要的测试用例
3. 更新相关文档
4. 提交信息清晰明确

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目维护者：[2lodoss]
- 邮箱：[1937305367@qq.com]
- 问题反馈：[Issues](https://github.com/2lodoss/Huaxuncheck/issues)

## 致谢

感谢以下开源项目：

- [Netmiko](https://github.com/ktbyers/netmiko)
- [Flask](https://github.com/pallets/flask)
- [Vue.js](https://github.com/vuejs/vue)
- [Element UI](https://github.com/ElemeFE/element)

## 安全说明

⚠️ **重要安全提示**：
- 请勿在生产环境中使用默认密码
- 定期更新设备密码
- 限制系统访问权限
- 定期备份数据库

## 常见问题

1. **Q: 系统支持哪些设备类型？**
   A: 目前支持Huawei VRP、H3C Comware和Ruijie OS等设备类型，Cisco等设备因为没条件测试，可能还不行

2. **Q: 如何添加新的设备类型？**
   A: 需要修改后端代码中的设备类型处理逻辑，并添加相应的前端选项。

3. **Q: 巡检结果如何保存？**
   A: 巡检结果会自动保存到数据库中，可以通过界面查看历史记录。

4. **Q: 系统支持批量操作吗？**
   A: 是的，支持批量导入设备信息和批量执行巡检。

## 更新日志

### v1.0.0 (2025-04-10)
- 初始版本发布
- 支持多种网络设备类型
- 设备分组管理功能
- 巡检结果记录和导出
---


## 如果您发现任何安全问题，请通过以下方式联系我

💬 微信公众号: 曦林听雨
💬 邮箱:1937305367@qq.com




