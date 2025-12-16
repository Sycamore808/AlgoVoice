# Github 仓库权限设置指南 🔒

## ✅ 已完成的工作

1. ✅ 删除了所有论文文档（docs/paper/）
2. ✅ 隐藏了所有AI模型相关敏感信息
3. ✅ 移除了性能数据和详细技术栈
4. ✅ 项目现在只包含核心代码

---

## ⚠️ 重要提示：Github公开仓库的限制

**Github的现实情况：**
- ❌ 公开仓库**无法完全阻止**他人下载（clone）代码
- ✅ 但可以限制其他操作，增加使用门槛

**如果不想被下载，只有两个选择：**
1. **设为Private私有仓库**（只有你授权的人能访问）
2. **使用Github Sponsors或付费墙**（需要付费才能访问）

---

## 🔧 推荐的设置方案

### 方案1：公开但添加使用限制 ⭐ 推荐

**优点**：增加曝光度，展示技术实力，同时设置使用门槛

**具体设置步骤：**

#### 1. 访问仓库设置
```
https://github.com/Sycamore808/AlgoVoice/settings
```

#### 2. 启用 Issues（支持评论）
- 找到 **"Features"** 部分
- ✅ 勾选 **"Issues"**
- 用户可以在这里提问、报告问题

#### 3. 启用 Discussions（支持讨论）
- ✅ 勾选 **"Discussions"**
- 创建更深入的技术讨论区

#### 4. 禁用 Fork（减少复制）
- ❌ 取消勾选 **"Allow forking"**
- 这样别人无法直接Fork你的仓库
- **但仍然可以clone下载代码**

#### 5. 设置 Branch Protection（保护主分支）
- 进入 **Settings → Branches**
- 添加规则保护 `main` 分支：
  - ✅ Require pull request reviews
  - ✅ Dismiss stale pull request approvals
  - ✅ Require review from Code Owners

#### 6. 添加严格的 LICENSE
在根目录创建 `LICENSE` 文件，使用限制性协议：

**推荐：GNU AGPL v3.0**
- 要求任何使用代码的人必须开源
- 商业使用需要授权

**或：专有许可证**
```
Copyright (c) 2025 Sycamore808

本软件仅供查看和学习使用。未经明确书面许可，禁止：
- 复制、修改、合并、发布、分发本软件
- 用于商业目的
- 再许可或出售本软件副本

联系方式：[你的邮箱]
```

#### 7. 添加使用声明（README开头）
```markdown
## ⚠️ 重要声明

**本项目采用专有许可证，仅供学习和技术交流使用。**

- ❌ 禁止商业使用
- ❌ 禁止未经授权的复制和分发
- ✅ 如需合作或商业授权，请通过 Issues 联系

查看完整许可证：[LICENSE](LICENSE)
```

---

### 方案2：Private私有仓库 🔒

**如果真的不想被下载：**

1. 进入仓库 Settings
2. 滚动到底部 **"Danger Zone"**
3. 点击 **"Change visibility"**
4. 选择 **"Make private"**

**私有仓库的限制：**
- ❌ 其他人无法查看代码
- ✅ 你可以邀请特定的人作为协作者
- ✅ 可以设置不同权限级别（Read, Write, Admin）

**邀请协作者：**
- Settings → Collaborators and teams
- 点击 **"Add people"**
- 输入Github用户名

---

### 方案3：混合方案（部分公开）

1. **创建两个仓库：**
   - `AlgoVoice-Public`：公开版本，只包含文档和Demo
   - `AlgoVoice-Private`：私有版本，包含完整代码

2. **公开版本只展示：**
   - README和项目介绍
   - 使用文档
   - Demo视频/截图
   - 联系方式

---

## 📧 如何处理申请加入的请求

### 设置 CONTRIBUTING.md

创建 `CONTRIBUTING.md` 文件：

```markdown
# 贡献指南

感谢您对 AlgoVoice 的兴趣！

## 如何参与

本项目目前处于**受限访问**状态。如需参与开发或获取完整代码访问权限，请：

1. **提交申请**：在 [Issues](https://github.com/Sycamore808/AlgoVoice/issues) 中创建新issue
2. **说明用途**：简要说明您的使用目的和技术背景
3. **等待审核**：我们会在3个工作日内回复

## 联系方式

- **Github Issues**: [提交申请](https://github.com/Sycamore808/AlgoVoice/issues/new)
- **Email**: your-email@example.com
```

---

## 🎯 推荐设置（总结）

**对于你的情况，我建议：**

✅ **保持公开**（展示技术实力）  
✅ **禁用Fork**（减少直接复制）  
✅ **添加严格LICENSE**（法律保护）  
✅ **启用Issues和Discussions**（支持互动）  
✅ **在README添加使用声明**（明确限制）  

**这样可以：**
- ✅ 展示项目给潜在雇主/合作者
- ✅ 增加使用门槛和法律保护
- ✅ 支持评论和申请加入
- ⚠️ 但无法100%阻止下载（这是Github公开仓库的本质）

---

## 📝 接下来的步骤

1. 访问 https://github.com/Sycamore808/AlgoVoice/settings
2. 按照上面的步骤配置仓库
3. 创建 LICENSE 文件
4. 更新 README 添加使用声明
5. 创建 CONTRIBUTING.md

**需要我帮你生成这些文件吗？**

