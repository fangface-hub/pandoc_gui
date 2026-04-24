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

-- PlantUMLサーバ設定
local plantuml_use_server = false
local plantuml_server_url = "http://www.plantuml.com/plantuml"

-- Mermaidモード設定 (mmdc or browser)
local mermaid_mode = "mmdc"
-- ブラウザモードで処理したブロック数（handle_doc で参照）
local diagram_count = 0

-- Mermaid.jsのパス設定（スタンドアロン版を使用）
local mermaid_js_path = "mermaid/mermaid.min.js"

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

-- Base64エンコード関数（画像をdata URIとして埋め込むため）
local function base64_encode(filepath)
  if package.config:sub(1,1) == '\\' then
    -- Windows: PowerShellを使用してBase64エンコード
    local cmd = string.format('powershell -Command "[Convert]::ToBase64String([IO.File]::ReadAllBytes(\'%s\'))"', filepath)
    local handle = io.popen(cmd)
    if not handle then return nil end
    local result = handle:read("*a")
    handle:close()
    return result:gsub("%s+", "")
  else
    -- Unix-like
    local handle = io.popen(string.format('base64 "%s"', filepath))
    if not handle then return nil end
    local result = handle:read("*a")
    handle:close()
    return result:gsub("%s+", "")
  end
end

local function render_zoomable_image_html(src, alt)
  return string.format([[

<div style="margin: 10px 0;">
  <img src="%s" style="max-width: 600px; cursor: zoom-in; display: block;" onclick="showImageModal(this.src)" alt="%s" />
</div>
<script>
if (typeof showImageModal === 'undefined') {
  function showImageModal(src) {
    var modal = document.createElement('div');
    modal.style.cssText = 'position:fixed;top:0;left:0;width:100%%;height:100%%;background:rgba(0,0,0,0.9);z-index:9999;display:flex;align-items:center;justify-content:center;cursor:zoom-out;';
    modal.onclick = function() { document.body.removeChild(modal); };
    var img = document.createElement('img');
    img.src = src;
    img.style.cssText = 'max-width:90%%;max-height:90%%;background:white;';
    modal.appendChild(img);
    document.body.appendChild(modal);
  }
}
</script>]], src, alt)
end

local function handle_meta(meta)
  if meta.plantuml_server then
    plantuml_use_server = meta.plantuml_server == true or pandoc.utils.stringify(meta.plantuml_server) == "true"
  end
  if meta.plantuml_server_url then
    plantuml_server_url = trim_quotes(pandoc.utils.stringify(meta.plantuml_server_url))
  end
  if meta.plantuml_jar then
    plantuml_jar = trim_quotes(pandoc.utils.stringify(meta.plantuml_jar))
  end
  if meta.java_path then
    java_cmd = trim_quotes(pandoc.utils.stringify(meta.java_path))
  end
  if meta.mermaid_mode then
    mermaid_mode = trim_quotes(pandoc.utils.stringify(meta.mermaid_mode))
  end
  if meta.mermaid_js_path then
    mermaid_js_path = trim_quotes(pandoc.utils.stringify(meta.mermaid_js_path))
  end
  return meta
end

local function handle_code_block(el)
  -- Mermaid
  if el.classes:includes("mermaid") then
    -- browserモードの場合は、mermaid.jsを使うHTMLを出力
    if mermaid_mode == "browser" then
      -- ブロックを連番IDで識別
      diagram_count = diagram_count + 1
      local diagram_id = string.format("mermaid-%d", diagram_count)
      io.stderr:write(string.format("🌐 Mermaid browser mode: %s\n", diagram_id))
      -- HTML エスケープ
      local escaped = el.text:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;")
      return pandoc.RawBlock('html',
        string.format('<pre class="mermaid" id="%s">%s</pre>', diagram_id, escaped))
    end

    -- mmdcモード（従来の方法）
    local input = tmp(".mmd")
    local output = tmp(".svg")
    local f = io.open(input, "w")
    if not f then
      io.stderr:write(string.format("⚠️ Failed to create mermaid input file: %s\n", input))
      return nil
    end
    f:write(el.text)
    f:close()
    
    -- ファイルが正しく作成されたか確認
    if not file_exists(input) then
      io.stderr:write(string.format("⚠️ Mermaid input file was not created: %s\n", input))
      return nil
    end
    
    -- Windows環境ではcmdを使用してmmdcを実行
    local cmd
    if package.config:sub(1,1) == '\\' then
      -- Windows: パスをダブルクォートで囲む
      cmd = string.format('cmd /c mmdc -i "%s" -o "%s"', input, output)
    else
      -- Unix-like systems
      cmd = string.format('mmdc -i "%s" -o "%s"', input, output)
    end
    
    io.stderr:write(string.format("🔍 Executing mermaid command: %s\n", cmd))
    local ok = os.execute(cmd)
    io.stderr:write(string.format("🔍 Command exit code: %s\n", tostring(ok)))
    
    if not ok then 
      io.stderr:write(string.format("⚠️ mmdc failed (exit code: %s)\n", tostring(ok)))
      return nil
    end
    
    -- 出力ファイルが生成されたか確認
    if not file_exists(output) then
      io.stderr:write(string.format("⚠️ Mermaid output file was not created: %s\n", output))
      return nil
    end
    
    io.stderr:write(string.format("✅ Mermaid diagram created: %s\n", output))
    
    -- SVGファイルをBase64エンコードしてdata URIとして埋め込む
    io.stderr:write("🔍 Starting base64 encoding...\n")
    local base64_data = base64_encode(output)
    if base64_data and base64_data ~= "" then
      io.stderr:write(string.format("✅ Base64 encoded, length: %d\n", #base64_data))
      local data_uri = "data:image/svg+xml;base64," .. base64_data
      local html = render_zoomable_image_html(data_uri, "Mermaid Diagram")
      return pandoc.RawBlock('html', html)
    else
      -- Base64エンコードに失敗した場合は通常のファイルパスを返す
      io.stderr:write("⚠️ Failed to encode image to base64, using file path\n")
      return pandoc.Para({ pandoc.Image({}, output) })
    end
  end

  -- PlantUML
  if el.classes:includes("plantuml") then
    local input = tmp(".puml")
    local output = tmp(".svg")
    
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
    
    local actual_output
    
    -- PlantUMLサーバを使用する場合
    if plantuml_use_server then
      io.stderr:write(string.format("🌐 Using PlantUML server: %s\n", plantuml_server_url))
      
      -- curlコマンドを使用してPlantUMLサーバにリクエスト
      local cmd
      if package.config:sub(1,1) == '\\' then
        -- Windows
        cmd = string.format('curl -s -X POST -H "Content-Type: text/plain" --data-binary "@%s" "%s/svg" -o "%s"', 
                           input, plantuml_server_url, output)
      else
        -- Unix-like
        cmd = string.format('curl -s -X POST -H "Content-Type: text/plain" --data-binary "@%s" "%s/svg" -o "%s"', 
                           input, plantuml_server_url, output)
      end
      
      io.stderr:write(string.format("🔍 Executing: %s\n", cmd))
      local ok = os.execute(cmd)
      
      if not ok or not file_exists(output) then
        local error_msg = string.format("⚠️ PlantUML server request failed\nServer: %s\nCommand: %s", 
                                       plantuml_server_url, cmd)
        io.stderr:write(error_msg .. "\n")
        return pandoc.Div({
          pandoc.Para({ pandoc.Strong({ pandoc.Str("PlantUML Server Error:") }) }),
          pandoc.Para({ pandoc.Str(error_msg) }),
          pandoc.CodeBlock(el.text, { class = "plantuml" })
        }, { class = "plantuml-error", style = "border: 2px solid red; padding: 10px; background-color: #fff3cd;" })
      end
      
      actual_output = output
    else
      -- JAR方式を使用
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

      -- PlantUMLを実行（SVG形式で出力）
      local cmd = string.format('%s -jar "%s" -tsvg "%s" 2>&1', java_cmd, jar, input)
      
      -- Capture PlantUML output for better error reporting
      local handle = io.popen(cmd)
      local plantuml_output = ""
      if handle then
        plantuml_output = handle:read("*a")
        handle:close()
      end
      
      -- PlantUMLは入力ファイルと同じディレクトリに.svgを生成する
      -- input = "C:\...\diagram.puml" -> output = "C:\...\diagram.svg"
      actual_output = input:gsub("%.puml$", ".svg")
      
      -- Check if output was created (PlantUML returns 0 even on some failures)
      if not file_exists(actual_output) then
        local error_msg = string.format("⚠️ PlantUML execution failed\nCommand: %s\nJava: %s\nJAR: %s\nPlantUML output: %s", 
                                       cmd, java_cmd, jar, plantuml_output)
        io.stderr:write(error_msg .. "\n")
        return pandoc.Div({
          pandoc.Para({ pandoc.Strong({ pandoc.Str("PlantUML Execution Error:") }) }),
          pandoc.Para({ pandoc.Str(error_msg) }),
          pandoc.CodeBlock(el.text, { class = "plantuml" })
        }, { class = "plantuml-error", style = "border: 2px solid red; padding: 10px; background-color: #fff3cd;" })
      end
    end
    
    -- SVGファイルをBase64エンコードしてdata URIとして埋め込む
    local base64_data = base64_encode(actual_output)
    if base64_data and base64_data ~= "" then
      local data_uri = "data:image/svg+xml;base64," .. base64_data
      local html = render_zoomable_image_html(data_uri, "PlantUML Diagram")
      return pandoc.RawBlock('html', html)
    else
      -- Base64エンコードに失敗した場合は通常のファイルパスを返す
      return pandoc.Para({ pandoc.Image({}, actual_output) })
    end
  end
end

-- ドキュメント末尾にmermaid.jsローダースクリプトを追加（browser モード用）
local function handle_doc(doc)
  if mermaid_mode == "browser" and diagram_count > 0 then
    io.stderr:write(string.format("🌐 Adding mermaid finalizer script (%d block(s))\n", diagram_count))
    local modal_script_html = [[<script>
if (typeof window.showImageModal === 'undefined') {
  window.showImageModal = function(src) {
    var modal = document.createElement('div');
    modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:9999;display:flex;align-items:center;justify-content:center;cursor:zoom-out;';
    modal.onclick = function() { document.body.removeChild(modal); };
    var img = document.createElement('img');
    img.src = src;
    img.style.cssText = 'max-width:90%;max-height:90%;background:white;';
    modal.appendChild(img);
    document.body.appendChild(modal);
  };
}
</script>]]
    table.insert(doc.blocks, pandoc.RawBlock('html', modal_script_html))
    local script_html = string.format([[<script type="text/javascript">
(function() {
  var _self = document.currentScript;
  var _mjs  = document.createElement('script');
  _mjs.id   = 'pandoc-gui-mermaid-js';
  _mjs.src  = '%s';
  _mjs.onload = async function() {
    mermaid.initialize({ startOnLoad: false, securityLevel: 'loose' });
    var els = document.querySelectorAll('pre.mermaid');
    for (var i = 0; i < els.length; i++) {
      var el    = els[i];
      var diagId = el.id || ('mermaid-' + i);
      try {
        var res = await mermaid.render(diagId + '-svg', el.textContent.trim());
        var tmp = document.createElement('div');
        tmp.innerHTML = res.svg;
        var svg = tmp.firstChild;
        var container = document.createElement('div');
        container.style.margin = '10px 0';
        svg.style.display = 'block';
        svg.style.maxWidth = '600px';
        svg.style.cursor = 'zoom-in';
        svg.setAttribute('onclick', "showImageModal('data:image/svg+xml;charset=utf-8,' + encodeURIComponent(this.outerHTML))");
        container.appendChild(svg);
        el.parentNode.replaceChild(container, el);
      } catch(e) {
        console.error('[PandocGUI] Mermaid render error (' + diagId + '):', e);
      }
    }
    // mermaid.js スクリプトとこのスクリプトをDOMから除去
    var mjs = document.getElementById('pandoc-gui-mermaid-js');
    if (mjs) mjs.parentNode.removeChild(mjs);
    if (_self && _self.parentNode) _self.parentNode.removeChild(_self);
    // SVGインライン埋め込み済みHTMLを /save-html に POST して上書き
    var fname = decodeURIComponent(window.location.pathname.split('/').pop());
    try {
      var html = '<!DOCTYPE html>\n' + document.documentElement.outerHTML;
      var r = await fetch('/save-html', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ html: html, filename: fname })
      });
      if (r.ok) {
        console.log('[PandocGUI] SVGインライン埋め込みHTML保存完了: ' + fname);
      } else {
        console.warn('[PandocGUI] /save-html returned ' + r.status);
      }
    } catch(e) {
      console.error('[PandocGUI] /save-html failed:', e);
    }
  };
  document.body.appendChild(_mjs);
})();
</script>]], mermaid_js_path)
    table.insert(doc.blocks, pandoc.RawBlock('html', script_html))
  end
  return doc
end

return {
  { Meta = handle_meta },
  { CodeBlock = handle_code_block },
  { Pandoc = handle_doc }
}