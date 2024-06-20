import fitz


def split_pdf_by_keyword(input_pdf_path, output_pdf_path1, output_pdf_path2, keyword):
    # 打开输入的PDF文件
    input_pdf = fitz.open(input_pdf_path)
    
    # 创建两个新的PDF文件
    output_pdf1 = fitz.open()
    output_pdf2 = fitz.open()
    
    # 初始化状态变量
    keyword_found = False
    
    for page_num in range(input_pdf.page_count):
        page = input_pdf.load_page(page_num)
        text = page.get_text("text")
        lines = text.splitlines()
        
        if keyword in text and not keyword_found:
            keyword_found = True
            # 找到关键字所在的行索引
            keyword_line_index = next(i for i, line in enumerate(lines) if keyword in line)
            
            # 将关键字之前的内容添加到第一个输出PDF中
            new_page1 = output_pdf1.new_page(width=page.rect.width, height=page.rect.height)
            for line in lines[:keyword_line_index]:
                new_page1.insert_text((0, new_page1.rect.height - 20 * (keyword_line_index - lines.index(line))), line)
            
            # 将关键字及之后的内容添加到第二个输出PDF中
            new_page2 = output_pdf2.new_page(width=page.rect.width, height=page.rect.height)
            for line in lines[keyword_line_index:]:
                new_page2.insert_text((0, new_page2.rect.height - 20 * (len(lines) - lines.index(line))), line)
        else:
            # 在关键字找到之前，全部内容都添加到第一个输出PDF中
            if not keyword_found:
                new_page = output_pdf1.new_page(width=page.rect.width, height=page.rect.height)
                for line in lines:
                    new_page.insert_text((0, new_page.rect.height - 20 * (lines.index(line) + 1)), line)
            # 在关键字找到之后，全部内容都添加到第二个输出PDF中
            else:
                new_page = output_pdf2.new_page(width=page.rect.width, height=page.rect.height)
                for line in lines:
                    new_page.insert_text((0, new_page.rect.height - 20 * (lines.index(line) + 1)), line)
    
    # 保存分割后的PDF文件
    output_pdf1.save(output_pdf_path1)
    output_pdf2.save(output_pdf_path2)


# 示例用法
input_pdf_path = './output/国家及各省市营商环境政策汇编2023 - 101~103.pdf'
output_pdf_path1 = './output/国家及各省市营商环境政策汇编2023 - Part 1 中国.pdf'
output_pdf_path2 = './output/国家及各省市营商环境政策汇编2023 - Part 2 华北.pdf'
keyword = '二、华北'

split_pdf_by_keyword(input_pdf_path, output_pdf_path1, output_pdf_path2, keyword)
