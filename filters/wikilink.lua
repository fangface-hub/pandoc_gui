function Str(el)
  local text = el.text

  -- [[page|title]] 形式
  local page, title = text:match("%[%[([^|]+)|([^]]+)%]%]")
  if page and title then
    -- .md#id を .html#id に変換
    local converted_page = page:gsub("%.md(#[^#]*)", ".html%1")
    -- .md のみの場合も .html に変換
    if not converted_page:match("%.html") then
      converted_page = converted_page:gsub("%.md$", ".html")
    end
    -- 拡張子がない場合は .html を追加
    if not converted_page:match("%.html") then
      converted_page = converted_page .. ".html"
    end
    return pandoc.Link(title, converted_page)
  end

  -- [[page]] 形式
  page = text:match("%[%[([^]]+)%]%]")
  if page then
    -- .md#id を .html#id に変換
    local converted_page = page:gsub("%.md(#[^#]*)", ".html%1")
    -- .md のみの場合も .html に変換
    if not converted_page:match("%.html") then
      converted_page = converted_page:gsub("%.md$", ".html")
    end
    -- 拡張子がない場合は .html を追加
    if not converted_page:match("%.html") then
      converted_page = converted_page .. ".html"
    end
    return pandoc.Link(page, converted_page)
  end

  return el
end

-- 通常のMarkdownリンク [text](page.md) の変換
function Link(el)
  local target = el.target
  
  -- .md#id を .html#id に変換
  target = target:gsub("%.md(#[^#]*)", ".html%1")
  -- .md のみの場合も .html に変換
  target = target:gsub("%.md$", ".html")
  
  el.target = target
  return el
end