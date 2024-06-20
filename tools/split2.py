import fitz  # PyMuPDF

output_dir = './output/'
pdf_document = fitz.open('./input/国家及各省市营商环境政策汇编（2023）(1).pdf')
min_font_size = 15
titles = []

for page_num in range(pdf_document.page_count):
  page = pdf_document.load_page(page_num)
  blocks = page.get_text("dict")["blocks"]
  
  for block in blocks:
    if "lines" not in block:
      continue
    for line in block["lines"]:
      for span in line["spans"]:
        font_size = span["size"]
        text = span["text"]
        
        if font_size >= min_font_size:
          titles.append(text)

for title in titles:
  print(title)
  