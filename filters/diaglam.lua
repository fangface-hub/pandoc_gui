local tmp = require("pandoc.path").make_temp_file

-- 環境変数 PLANTUML_JAR またはメタデータ plantuml_jar で jar のパスを指定可能
local plantuml_jar = os.getenv("PLANTUML_JAR")  -- nil の場合は後で "plantuml.jar" を使用

-- java 実行ファイルはメタデータ java_path -> 環境変数 JAVA_PATH -> JAVA_HOME/bin/java -> "java"
local sep = package.config:sub(1,1)
local java_cmd = (os.getenv("JAVA_PATH")
                 or (os.getenv("JAVA_HOME") and (os.getenv("JAVA_HOME") .. sep .. "bin" .. sep .. "java"))
                 or "java")

local function file_exists(path)
  local f = io.open(path, "r")
  if f then f:close(); return true end
  return false
end

function Meta(meta)
  if meta.plantuml_jar then
    plantuml_jar = pandoc.utils.stringify(meta.plantuml_jar)
  end
  if meta.java_path then
    java_cmd = pandoc.utils.stringify(meta.java_path)
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
    io.open(input, "w"):write(el.text):close()
    local jar = plantuml_jar or "plantuml.jar"

    if not file_exists(jar) then
      io.stderr:write(string.format("plantuml jar not found: %s\n", jar))
      return nil
    end
    -- java 実行ファイルの存在チェック（"java" の場合はスキップ）
    if java_cmd ~= "java" and not file_exists(java_cmd) then
      io.stderr:write(string.format("java executable not found: %s\n", java_cmd))
      return nil
    end

    local cmd = string.format('"%s" -jar "%s" -tpng "%s" -o "%s"', java_cmd, jar, input, output)
    local ok = os.execute(cmd)
    if not ok then io.stderr:write(string.format("plantuml failed (java=%s jar=%s): %s\n", java_cmd, jar, tostring(ok))) end
    return pandoc.Para({ pandoc.Image({}, output) })
  end
end