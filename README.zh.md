# Pandoc GUI

[English](README.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [한국어](README.ko.md)

一个简单的Pandoc GUI前端，使用Lua过滤器生成图表（Mermaid、PlantUML等）。专为Windows设计。

## 功能特性

- 文件/文件夹选择和输出目标设置
- 应用`filters/`目录中的Lua过滤器（预设+用户添加）
- CSS样式设置（在`stylesheets/`目录中），可选择嵌入或外部链接
- 保存/加载配置文件（`profiles/*.json`）
- 日志输出（GUI和`pandoc.log`）
- 在后台运行Pandoc，应用退出时安全终止子进程

## 系统要求

- Python 3.8+
- Pandoc（添加到PATH）
- Mermaid需要：`mmdc`（mermaid-cli）
- PlantUML需要：`plantuml.jar`和Java（jdk/jre）
- （可选）所需的Lua过滤器（`filters/*.lua`）

## 运行方法

1. 安装所需工具（Pandoc、Node/mmdc、Java等）
2. 从仓库根目录运行：

    ```powershell
    python main_window.py
    ```

## 指定PlantUML / Java路径

使用以下方法指定PlantUML JAR和Java可执行文件（按优先级顺序）：

- PlantUML JAR：文档YAML元数据`plantuml_jar` → 环境变量`PLANTUML_JAR` → `plantuml.jar`
- Java可执行文件：文档YAML元数据`java_path` → 环境变量`JAVA_PATH` → `JAVA_HOME\bin\java` → `java`（PATH）

Windows环境变量示例（命令提示符）：

```bat
set PLANTUML_JAR=C:\path\to\plantuml.jar
set JAVA_PATH=C:\path\to\java.exe
```

PowerShell：

```powershell
$env:PLANTUML_JAR = 'C:\path\to\plantuml.jar'
$env:JAVA_PATH = 'C:\path\to\java.exe'
```

文档中的YAML指定示例：

```yaml
---
plantuml_jar: C:\path\to\plantuml.jar
java_path: C:\path\to\java.exe
---
```

## 使用方法（GUI）

1. 使用"文件选择"或"文件夹选择"选择输入
2. 使用"输出目标选择"选择输出目录
3. 添加预设/用户过滤器（使用上下按钮调整顺序）
4. （可选）配置排除模式以在文件夹转换期间跳过特定文件
5. 点击"运行转换"

### 排除模式设置

批量转换文件夹时，可以排除特定文件或文件夹：

- 点击"排除模式管理"打开设置
- 支持通配符模式（例如：`*.tmp`、`__pycache__`、`.git`）
- 支持多个模式（每行一个）

模式匹配示例：

- `*.tmp` - 排除所有.tmp文件
- `__pycache__` - 排除__pycache__文件夹及其内容
- `.git` - 排除.git文件夹
- `test_*` - 排除以test_开头的文件
- `*_backup` - 排除以_backup结尾的文件

## 日志和配置文件

- GUI显示日志，系统在`pandoc.log`中记录详细信息
- 系统将配置文件保存为`profiles/`目录中的JSON格式

## 创建分发包

### 使用PyInstaller创建文件夹分发

1. 安装PyInstaller：

    ```powershell
    pip install pyinstaller
    ```

2. 创建可执行文件：

    **注意**：仓库中包含`PandocGUI.spec`，已配置构建后处理，将`filters/`和`locales/`放置在`_internal/`之外。

    ```powershell
    python -m PyInstaller PandocGUI.spec
    ```

    仅在需要重新生成`.spec`文件时（通常不需要）：

    ```powershell
    pyinstaller --noconsole --onedir --name "PandocGUI" `
      --add-data "locales;locales" `
      --add-data "filters;filters" `
      --add-data "stylesheets;stylesheets" `
      main_window.py
    ```

    **重要**：必须手动将构建后处理添加到上述命令生成的`.spec`文件中。

3. 构建输出位于`dist/PandocGUI/`：

    ```text
    dist/PandocGUI/
    ├── PandocGUI.exe        # 可执行文件
    ├── filters/             # Lua过滤器
    ├── locales/             # 翻译文件
    ├── stylesheets/         # CSS样式表
    ├── help/                # 帮助文件（HTML）
    ├── profiles/            # 配置文件（运行时创建）
    └── _internal/           # Python依赖项
    ```

    `.spec`文件中的构建后处理将`filters/`、`locales/`和`stylesheets/`放置在`_internal/`之外

### 使用MSIX Packaging Tool创建Windows安装程序

1. 安装MSIX Packaging Tool：

   - 从Microsoft Store安装"MSIX Packaging Tool"

2. 启动MSIX Packaging Tool并选择"Application package"

3. 选择"Create package on this computer"

4. 输入包信息：

    - Package name：`PandocGUI`
    - Publisher：`CN=YourName`（根据证书更改）
    - Version：`1.0.0.0`

5. 选择安装程序：

    - 点击"Browse"并选择`dist/PandocGUI/PandocGUI.exe`
    - Installation location：`C:\Program Files\PandocGUI`

6. 执行安装并捕获：

   - 启动应用并验证操作
   - 验证所有必需文件都已包含
   - 点击"Done"

7. 保存包：

    - 另存为.msix文件

8. 签名（可选）：

    - 创建测试证书或使用现有证书

    ```powershell
    # 创建测试证书
    New-SelfSignedCertificate -Type Custom -Subject "CN=YourName" `
      -KeyUsage DigitalSignature -FriendlyName "PandocGUI Test Certificate" `
      -CertStoreLocation "Cert:\CurrentUser\My" `
      -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
    
    # 签名MSIX文件
    SignTool sign /fd SHA256 /a /f certificate.pfx /p password PandocGUI.msix
    ```

9. 分发安装程序：

   - 分发.msix文件
   - 用户在安装应用之前先安装证书

### 注意事项

- 验证资源文件（如`filters/`和`locales/`）是否正确包含
- 外部工具（如Pandoc、mmdc和Java）需要单独安装
- MSIX包需要签名（开发期间可以使用测试证书）

## 测试

我们提供了单元测试。使用以下命令运行：

### 运行所有测试

```powershell
python -m unittest discover -s . -p "test_*.py"
```

### 运行单个测试文件

```powershell
python -m unittest test_<name>.py
```

示例：

```powershell
python -m unittest test_main_window.py
```

### 详细测试输出

```powershell
python -m unittest discover -v
```

测试文件：

- `test_main_window.py` - 主窗口和配置文件管理功能
- `test_css_window.py` - CSS设置功能
- `test_filter_window.py` - 过滤器管理功能
- `test_log_window.py` - 日志显示功能

## 故障排除

- 如果系统找不到PlantUML或无法执行Java，stderr中会出现消息。使用环境变量或YAML元数据指定路径。
- 系统在GUI日志和`pandoc.log`中显示Pandoc错误。

## 开发说明

- 我们将Lua过滤器放在`filters/`目录中（例如：`filters/diagram.lua`）。
- 我们将CSS文件放在`stylesheets/`目录中。您可以从GUI中选择它们，并将其应用为嵌入或外部链接。
- 系统在后台线程中执行转换，并在应用退出时终止/结束子进程。
