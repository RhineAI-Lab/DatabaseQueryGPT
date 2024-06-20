import fitz  # PyMuPDF
import re
import os




def split_pdf_by_title(input_pdf, output_dir):
  # 确保输出目录存在
  os.makedirs(output_dir, exist_ok=True)
  
  # 打开PDF文件
  pdf_document = fitz.open(input_pdf)
  
  # 初始化变量
  output_files = []
  current_title = None
  current_doc = None
  
  # 遍历每一页
  for page_num in range(pdf_document.page_count):
    page = pdf_document.load_page(page_num)
    text = page.get_text("text")
    
    # 使用正则表达式匹配标题
    match = re.search(title_pattern, text)
    if match:
      # 保存当前的PDF文档
      if current_doc:
        current_doc.save(f"{output_dir}/{current_title}.pdf")
        current_doc.close()
        output_files.append(f"{output_dir}/{current_title}.pdf")
      
      # 创建新的PDF文档
      current_title = match.group(0).strip().replace("/", "_").replace("\\", "_")
      current_doc = fitz.open()
    
    # 将当前页添加到当前PDF文档
    if current_doc:
      current_doc.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
  
  # 保存最后一个PDF文档
  if current_doc:
    current_doc.save(f"{output_dir}/{current_title}.pdf")
    current_doc.close()
    output_files.append(f"{output_dir}/{current_title}.pdf")
  
  return output_files


# 示例用法
input_pdf = './input/国家及各省市营商环境政策汇编（2023）(1).pdf'
output_dir = './output/'
output_files = split_pdf_by_title(input_pdf, output_dir)

print("生成的PDF文件：")
for output_file in output_files:
  print(output_file)


