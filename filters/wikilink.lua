function Str(el)
  local text = el.text

  local page, title = text:match("%[%[(|]+)|(]+)%]%]")
  if page and title then
    return pandoc.Link(title, page .. ".html")
  end

  page = text:match("%[%[(]+)%]%]")
  if page then
    return pandoc.Link(page, page .. ".html")
  end

  return el
end