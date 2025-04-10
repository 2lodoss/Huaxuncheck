# 网络设备巡检系统 (Network Inspection System)

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Netmiko](https://img.shields.io/badge/netmiko-4.1.2-blue.svg)](https://github.com/ktbyers/netmiko)

一个简单易用的网络设备自动化巡检工具，支持多种网络设备（思科、华为、H3C、锐捷等）。

## 功能特点

- 🚀 支持多种网络设备类型（Cisco、Huawei、H3C、Ruijie等）
- 🔄 自动执行预设命令获取设备状态和配置
- 📊 设备分组管理
- 📝 巡检结果记录和导出
- 📱 简洁直观的Web界面
- 🔒 支持SSH和Telnet连接
- 📦 支持设备信息批量导入/导出

## 快速开始

### 环境要求

- Python 3.6+
- 依赖包（见requirements.txt）

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/yourusername/network-inspection-system.git
cd network-inspection-system
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动系统
```bash
python app.py
```

4. 访问系统
打开浏览器访问：http://localhost:5000

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
network-inspection-system/
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
- 邮箱：[2lodoss@gmail.com]
- 问题反馈：[Issues](https://github.com/yourusername/network-inspection-system/issues)

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
   A: 目前支持Cisco IOS、Cisco NX-OS、Juniper JunOS、Huawei VRP、H3C Comware和Ruijie OS等设备类型。

2. **Q: 如何添加新的设备类型？**
   A: 需要修改后端代码中的设备类型处理逻辑，并添加相应的前端选项。

3. **Q: 巡检结果如何保存？**
   A: 巡检结果会自动保存到数据库中，可以通过界面查看历史记录。

4. **Q: 系统支持批量操作吗？**
   A: 是的，支持批量导入设备信息和批量执行巡检。

## 更新日志

### v1.0.0 (2023-XX-XX)
- 初始版本发布
- 支持多种网络设备类型
- 设备分组管理功能
- 巡检结果记录和导出

---

