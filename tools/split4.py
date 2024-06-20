from PyPDF2 import PdfReader, PdfWriter

# 打开原始PDF文件
input_pdf_path = './input/国家及各省市营商环境政策汇编（2023）(1).pdf'
output_pdf_path = './output/国家及各省市营商环境政策汇编2023 - Part 8 西北.pdf'

# 读取PDF文件
reader = PdfReader(input_pdf_path)
writer = PdfWriter()

# 0 102 302 833 1038 1230 1316 1479 1747
for page_num in range(1478, 1747):
    page = reader.pages[page_num]
    writer.add_page(reader.pages[page_num])

# 写入到新的PDF文件
with open(output_pdf_path, 'wb') as output_pdf:
    writer.write(output_pdf)

print(f'新PDF文件已保存到 {output_pdf_path}')
