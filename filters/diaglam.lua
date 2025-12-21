-- ダブルクォートをトリムする関数
local function trim_quotes(str)
  if not str then return str end
  -- 先頭と末尾のダブルクォートを削除（非貪欲マッチ）
  local trimmed = str:match('^"(.*)"$')
  if trimmed then return trimmed end
  -- シングルクォートも削除（念のため）
  trimmed = str:match("^'(.*)'$")
  if trimmed then return trimmed end
  return str
end

-- 一時ファイル作成関数（Pandoc 3.0以降とそれ以前の互換性対応）
local tmp_counter = 0
local tmp
if pandoc.path and pandoc.path.make_temp_file then
  -- Pandoc 3.0以降
  tmp = function(suffix)
    return pandoc.path.make_temp_file(suffix or "")
  end
else
  -- Pandoc 2.x以前: 手動で一時ファイルパスを生成
  tmp = function(suffix)
    local tmpdir = os.getenv("TEMP") or os.getenv("TMP") or os.getenv("TMPDIR") or "/tmp"
    tmp_counter = tmp_counter + 1
    local name = string.format("%s%spandoc_diagram_%d_%d%s", 
                               tmpdir, 
                               package.config:sub(1,1),
                               os.time(),
                               tmp_counter,
                               suffix or "")
    return name
  end
end

-- 環境変数 PLANTUML_JAR またはメタデータ plantuml_jar で jar のパスを指定可能
local plantuml_jar = trim_quotes(os.getenv("PLANTUML_JAR"))  -- nil の場合は後で "plantuml.jar" を使用

-- java 実行ファイルはメタデータ java_path -> 環境変数 JAVA_PATH -> JAVA_HOME/bin/java -> "java"
local sep = package.config:sub(1,1)
local java_cmd = trim_quotes(os.getenv("JAVA_PATH")
                 or (os.getenv("JAVA_HOME") and (os.getenv("JAVA_HOME") .. sep .. "bin" .. sep .. "java"))
                 or "java")

local function file_exists(path)
  if not path then return false end
  local f = io.open(path, "r")
  if f then f:close(); return true end
  return false
end

function Meta(meta)
  if meta.plantuml_jar then
    plantuml_jar = trim_quotes(pandoc.utils.stringify(meta.plantuml_jar))
  end
  if meta.java_path then
    java_cmd = trim_quotes(pandoc.utils.stringify(meta.java_path))
  end
  return meta
end

function CodeBlock(el)
  -- Mermaid
  if el.classes:includes("mermaid") then
    local input = tmp(".mmd")
    local output = tmp(".png")
    io.open(input, "w"):write(el.text):close()
    local cmd = string.format('mmdc -i "%s" -o "%s"', input, output)
    local ok = os.execute(cmd)
    if not ok then io.stderr:write("mmdc failed: " .. tostring(ok) .. "\n") end
    return pandoc.Para({ pandoc.Image({}, output) })
  end

  -- PlantUML
  if el.classes:includes("plantuml") then
    local input = tmp(".puml")
    local output = tmp(".png")
    
    -- ファイルを書き込む
    local f = io.open(input, "w")
    if not f then
      io.stderr:write(string.format("⚠️ Failed to create input file: %s\n", input))
      return nil
    end
    f:write(el.text)
    f:close()
    
    -- ファイルが正しく作成されたか確認
    if not file_exists(input) then
      io.stderr:write(string.format("⚠️ Input file was not created: %s\n", input))
      return nil
    end
    
    local jar = plantuml_jar or "plantuml.jar"

    if not file_exists(jar) then
      local error_msg = string.format("⚠️ PlantUML JAR not found: %s\nPlease set plantuml_jar path in settings.", jar)
      io.stderr:write(error_msg .. "\n")
      -- エラーメッセージを含むコードブロックとして返す
      return pandoc.Div({
        pandoc.Para({ pandoc.Strong({ pandoc.Str("PlantUML Error:") }) }),
        pandoc.Para({ pandoc.Str(error_msg) }),
        pandoc.CodeBlock(el.text, { class = "plantuml" })
      }, { class = "plantuml-error", style = "border: 2px solid red; padding: 10px; background-color: #fff3cd;" })
    end
    
    -- java 実行ファイルの存在チェック（"java" の場合はスキップ）
    if java_cmd ~= "java" and not file_exists(java_cmd) then
      local error_msg = string.format("⚠️ Java executable not found: %s\nPlease set java_path in settings or install Java.", java_cmd)
      io.stderr:write(error_msg .. "\n")
      return pandoc.Div({
        pandoc.Para({ pandoc.Strong({ pandoc.Str("PlantUML Error:") }) }),
        pandoc.Para({ pandoc.Str(error_msg) }),
        pandoc.CodeBlock(el.text, { class = "plantuml" })
      }, { class = "plantuml-error", style = "border: 2px solid red; padding: 10px; background-color: #fff3cd;" })
    end

    -- PlantUMLを実行（-oオプションは出力ディレクトリのみ、ファイル名は自動生成）
    local cmd = string.format('%s -jar "%s" -tpng "%s" 2>&1', java_cmd, jar, input)
    
    -- Capture PlantUML output for better error reporting
    local handle = io.popen(cmd)
    local plantuml_output = ""
    if handle then
      plantuml_output = handle:read("*a")
      handle:close()
    end
    
    -- PlantUMLは入力ファイルと同じディレクトリに.pngを生成する
    -- input = "C:\...\diagram.puml" -> output = "C:\...\diagram.png"
    local actual_output = input:gsub("%.puml$", ".png")
    
    -- Check if output was created (PlantUML returns 0 even on some failures)
    if not file_exists(actual_output) then
      local error_msg = string.format("⚠️ PlantUML execution failed\nCommand: %s\nJava: %s\nJAR: %s\nPlantUML output: %s", cmd, java_cmd, jar, plantuml_output)
      io.stderr:write(error_msg .. "\n")
      return pandoc.Div({
        pandoc.Para({ pandoc.Strong({ pandoc.Str("PlantUML Execution Error:") }) }),
        pandoc.Para({ pandoc.Str(error_msg) }),
        pandoc.CodeBlock(el.text, { class = "plantuml" })
      }, { class = "plantuml-error", style = "border: 2px solid red; padding: 10px; background-color: #fff3cd;" })
    end
    
    return pandoc.Para({ pandoc.Image({}, actual_output) })
  end
end