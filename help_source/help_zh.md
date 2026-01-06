---
lang: zh
---

# PandocGUI 帮助

## 概述

PandocGUI 是一个简单的 GUI 工具，用于使用 Pandoc 将 Markdown 文件转换为 HTML 和其他格式。它可以使用 Lua 过滤器自动生成 Mermaid 和 PlantUML 等图表。

## 主要功能

- **文件/文件夹转换**：转换单个文件或批量处理文件夹中的多个文件
- **Lua 过滤器**：应用 diagram.lua 等过滤器来生成图表
- **CSS 样式**：应用自定义样式表（嵌入/外部链接）
- **配置文件管理**：保存和加载常用设置
- **排除模式**：在文件夹转换期间跳过特定文件
- **日志显示**：监控转换进度和错误

## 基本用法

### 1. 选择输入

**转换文件：**

1. 点击"文件选择"按钮
2. 选择要转换的 Markdown 文件（.md）

**批量转换文件夹：**

1. 点击"文件夹选择"按钮
2. 选择包含 Markdown 文件的文件夹
3. 子文件夹中的文件将自动处理

### 2. 设置输出目标

1. 点击"输出目标选择"按钮
2. 选择保存转换后文件的文件夹

### 3. 配置过滤器

**添加预设过滤器：**

1. 从"预设过滤器"下拉菜单中选择
2. 点击"添加"按钮

**添加用户过滤器：**

1. 点击"浏览"按钮选择 `.lua` 文件
2. 点击"添加"按钮

**更改过滤器顺序：**

- 在过滤器列表中选择项目
- 使用"↑""↓"按钮调整顺序

**删除过滤器：**

- 在过滤器列表中选择项目
- 点击"删除"按钮

### 4. 配置 CSS 样式

1. 点击"CSS 样式表设置"按钮
2. 选择 CSS 文件
3. 选择应用方法：
   - **嵌入**：将 CSS 嵌入 HTML 文件中
   - **外部链接**：作为单独文件输出并从 HTML 链接

### 5. 配置排除模式（用于文件夹转换）

要在文件夹转换期间跳过特定文件：

1. 点击"排除模式管理"按钮
2. 排除模式窗口打开
3. 输入模式（每行一个）
4. 点击"确定"

**模式示例：**

```text
*.tmp
__pycache__
.git
test_*
*_backup
node_modules
```

### 6. 执行转换

1. 验证所有设置
2. 点击"运行转换"按钮
3. 在日志窗口中检查进度

## 配置文件功能

您可以将常用的设置组合保存为配置文件。

### 创建配置文件

1. 点击"添加"按钮
2. 输入新配置文件名称
3. 点击"确定"
4. 默认配置文件设置将被复制

### 选择配置文件

1. 从配置文件下拉菜单中选择
2. 设置将自动加载

### 保存配置文件

1. 调整设置
2. 从下拉菜单中选择目标配置文件
3. 点击"保存"按钮
4. 当前设置将保存到配置文件

### 删除配置文件

1. 从下拉菜单中选择要删除的配置文件
2. 点击"删除"按钮
3. 在确认对话框中点击"是"

**注意:** 默认配置文件无法删除。

### 更新配置文件

1. 点击"加载"按钮
2. 配置文件将使用最新的设置项更新（向后兼容性）

保存的配置文件以 JSON 格式存储在 `profiles/` 文件夹中。

## PlantUML / Java 配置

使用 PlantUML 图表时，有两种执行方法可用。

### 选择 PlantUML 执行方法

**JAR方式（本地执行）：**

1. 在"执行方法"中选择"JAR文件"
2. 指定 Java 可执行文件路径
3. 指定 PlantUML JAR 文件路径

**服务器方式（在线执行）：**

1. 在"执行方法"中选择"服务器"
2. 指定 PlantUML 服务器 URL（默认：<http://www.plantuml.com/plantuml>）
3. 不需要 Java/JAR 文件

### PlantUML JAR 方式配置

按以下优先级顺序搜索路径：

#### PlantUML JAR 文件

1. GUI 设置路径
2. 文档中的 YAML 元数据 `plantuml_jar`
3. 环境变量 `PLANTUML_JAR`
4. 默认值 `plantuml.jar`

#### Java 可执行文件

1. GUI 设置路径
2. 文档中的 YAML 元数据 `java_path`
3. 环境变量 `JAVA_PATH`
4. 环境变量 `JAVA_HOME\bin\java`
5. 从 PATH 中的 `java`

### 环境变量配置示例

**PowerShell：**

```powershell
$env:PLANTUML_JAR = 'C:\tools\plantuml.jar'
$env:JAVA_PATH = 'C:\Program Files\Java\jdk-17\bin\java.exe'
```

**命令提示符：**

```bat
set PLANTUML_JAR=C:\tools\plantuml.jar
set JAVA_PATH=C:\Program Files\Java\jdk-17\bin\java.exe
```

### YAML 元数据规范

在 Markdown 文件开头添加：

```yaml
---
plantuml_jar: C:\tools\plantuml.jar
java_path: C:\Program Files\Java\jdk-17\bin\java.exe
---
```

**使用服务器方式时：**

```yaml
---
plantuml_server: true
plantuml_server_url: http://www.plantuml.com/plantuml
---
```

### Mermaid 配置

生成 Mermaid 图表有两种方法：

#### 浏览器模式（默认，推荐）

**特点：**

- 无需安装命令行工具
- 使用浏览器和 mermaid.js 自动生成图表
- 使用本地 HTTP 服务器自动保存 SVG 文件

**使用方法：**

- 在 GUI 设置中选择"浏览器"作为 Mermaid 方法（默认）
- 转换期间浏览器会自动打开并生成图表
- SVG 文件会自动保存到输出文件夹

**优点：**

- 无需设置
- 访问最新的 Mermaid.js 功能
- 环境独立

#### mmdc 模式（命令行工具）

**特点：**

- 使用 mermaid-cli (`mmdc`)
- 无头生成图表

**使用方法：**

- 在 GUI 设置中选择"mmdc"作为 Mermaid 方法
- 验证是否安装了 `mmdc`
- 在命令提示符中运行 `mmdc --version` 进行确认

**安装：**

```bash
npm install -g @mermaid-js/mermaid-cli
```

### 在 YAML 元数据中指定 Mermaid 模式

在 Markdown 文件开头添加：

```yaml
---
mermaid_mode: browser  # 或 mmdc
---
```

## 自动更新功能

当您更新应用程序时，以下文件将自动更新：

### 过滤器文件

- `filters/` 文件夹中的内置过滤器 (diaglam.lua, md2html.lua, wikilink.lua)
- 更新时自动更新到最新版本
- 用户添加的自定义过滤器受保护

### 配置文件设置

- 新版本中添加的新设置将自动补充
- 现有设置将保留
- 默认值从 `profiles/default.json` 获取

## 故障排除

### 找不到 Pandoc

**症状：**

- 启动时显示警告对话框
- 无法执行转换

**解决方案：**

1. 安装 Pandoc：<https://pandoc.org/installing.html>
2. 安装后，验证它是否添加到 PATH
3. 在命令提示符中运行 `pandoc --version` 进行确认

### 转换失败

**检查：**

- Pandoc 是否已安装并添加到 PATH？
- 输入文件是否为正确的 Markdown 格式？
- 您是否对输出文件夹有写权限？

**检查日志：**

- 在 GUI 日志窗口中检查错误消息
- 在 `pandoc.log` 文件中检查详细信息

### 图表未生成

**对于 Mermaid 图表（mmdc 模式）：**

- 验证是否安装了 `mmdc`（mermaid-cli）
- 在命令提示符中运行 `mmdc --version` 进行确认

**对于 Mermaid 图表（浏览器模式）：**

- 浏览器模式无需额外设置即可工作
- 检查浏览器是否自动打开
- 验证 SVG 文件是否保存到输出文件夹

**对于 PlantUML 图表：**

**JAR方式：**

- 验证 `plantuml.jar` 是否存在
- 验证是否安装了 Java
- 在 GUI 设置、环境变量或 YAML 元数据中指定路径

**服务器方式：**

- 验证互联网连接
- 验证服务器 URL 是否正确（默认：<http://www.plantuml.com/plantuml>）
- 检查防火墙设置

### 过滤器未应用

**检查：**

- 过滤器是否正确添加？（检查过滤器列表）
- Lua 文件是否存在于正确的路径？
- 过滤器顺序是否合适？（diagram.lua 可能需要特定顺序）

### 排除模式不起作用

**检查：**

- 模式语法是否正确？（使用通配符 `*`）
- 模式是否与文件名或文件夹名匹配？
- 您是否通过在排除模式窗口中点击"确定"来保存？

## 常见问题

### 问：我可以转换为哪些文件格式？

答：您可以转换为 Pandoc 支持的所有格式。主要格式包括：

- HTML
- PDF（需要 LaTeX）
- DOCX（Word）
- EPUB
- 许多其他格式

可以使用 Pandoc 选项指定输出格式（计划在未来版本中支持）。

### 问：我可以使用多个 CSS 文件吗？

答：当前版本仅支持一个 CSS 文件。如果需要多个样式，请合并 CSS 文件。

### 问：文件夹转换时是否保留文件结构？

答：是的，输入文件夹的子文件夹结构在输出目标中保留。

### 问：我可以取消转换吗？

答：您可以通过关闭窗口安全地终止转换过程。正在处理的文件将完成，但其余文件将被取消。

## 日志文件

转换详细信息记录在以下日志文件中：

- **位置**：`pandoc.log`（与可执行文件在同一文件夹中）
- **内容**：Pandoc 输出、错误消息、过滤器执行结果

如果出现问题，请检查此日志文件。

## 附录：关于过滤器

### 预设过滤器

放置在 `filters/` 文件夹中的 Lua 过滤器会自动检测。

**diagram.lua：**

- 将 Mermaid、PlantUML 等代码块转换为图表

**md2html.lua：**

- 在 Markdown 中执行其他处理

**wikilink.lua：**

- 转换 Wiki 格式的链接

### 添加自定义过滤器

1. 在任意位置创建 `.lua` 文件
2. 点击"用户过滤器"部分的"浏览"按钮
3. 选择创建的 Lua 文件
4. 点击"添加"按钮

## 支持信息

如果问题未解决，请报告以下信息：

- 您使用的 PandocGUI 版本
- Pandoc 版本（`pandoc --version`）
- 错误消息（来自日志窗口或 `pandoc.log`）
- 执行的步骤
- 示例输入文件（如果可能）

---

**PandocGUI** - Pandoc 的简单 GUI 前端
