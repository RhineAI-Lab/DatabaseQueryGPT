from call import gpt4
from structure import get_structure_info, execute_sql
from PIL import Image


# 查一下宣桥镇政府下有哪些企业
# 查查 DASHENG科技有限公司 在2023年每个月的累计收入变化情况
# 对比看看 DASHENG科技有限公司 和 上海联合创富实业有限公司 在2023年每个月的累计收入


def inference(text):
  if len(text.strip()) == 0:
    yield '', None, '', '状态：正常'
  else:
    print('Input:', text)
    yield '', None, '', '状态：数据库表结构加载中...'
    print()
    structure = get_structure_info()
    prompt = f'''
下面是我MySQL数据库中表的结构，请你根据这个表的结构，帮我解决一些问题。

有时会需要用到多个表，有时只需一个表，请你自行判断，尽可能使用少的表。
解决问题时先理解问题，说出整体思路，再输出SQL语句。

结果放在```sql格式的代码块中，并且代码块中不要出现任何注释。

下面是表结构：{structure}

我的需求是：
{text}
    '''
    print(prompt)
    print()
    yield '', None, '', '状态：大模型推理中...'
    gpt_result = gpt4.call(prompt, system_prompt='你是个语言能力和逻辑理解能力很强的AI助手', print_in_stream=True)
    print()
    if '```sql' not in gpt_result:
      print('\nError: SQL Not Found')
      yield '', None, '', '状态：错误 - 推理结果无SQL信息'
    else:
      yield '', None, '', '状态：SQL执行中...'
      sql_query = gpt_result.split('```sql')[1].split('```')[0].strip()
      print(f'SQL:\n{sql_query}')
      print()
      query_result = execute_sql(sql_query)
      print('Query Result:')
      print(query_result)
      yield query_result, None, '', '状态：正在判断是否需要图表...'
      print()
      if len(query_result.strip()) == 0:
        print('\nError: SQL Execute Failed')
        yield query_result, None, '', '状态：错误 - SQL语句执行失败'
      else:
        print('\n')
        prompt = f'''
用户向一个大模型提出了以下问题：
{text}

程序会自动根据用户的问题去数据库中查询该问题的结果。
请问你认为这个问题的结果可以绘制一个图表吗？如折线图柱状图或热力图等等。
先简要说名原因，如果可以，请在回答中包含[YES]，如果不适合，请在回答中包含[NO]。
'''
        print(prompt)
        print()
        gpt_result_2 = gpt4.call(prompt, system_prompt='你是个语言能力和逻辑理解能力很强的AI助手', print_in_stream=True)
        print()
        need_table = 'YES' in gpt_result_2
        if not need_table:
          yield query_result, None, '', '状态：正在给出总结...'
          prompt = f'''
用户提出了以下要求：
{text}

程序在数据库中搜索到了该问题的对应信息结果：
{query_result}

并且我已经将数据展示在了上方。

现在请你和用户总结一下这个问题的回答，例如 “从上面的结果我们可以看出...” “综上所述...” 等。
回答要正式，我会直接把你回答的话给用户看，所以不要回复我，只需要跟用户说话。
          '''
          finally_gpt_result_4 = ''
          for gpt_result_4 in gpt4.call_generator(prompt, '你是个语言能力和逻辑理解能力很强的AI助手', True):
            finally_gpt_result_4 = gpt_result_4
            yield query_result, None, gpt_result_4, '状态：正在给出总结...'
          print()
          print('\nFinished.\n')
          yield query_result, None, finally_gpt_result_4, '状态：完成'
        else:
          yield query_result, None, '', '状态：正在绘制图表...'
          prompt = f'''
用户提出了以下要求：
{text}

程序在数据库中搜索到了该问题的对应信息结果：
{query_result}

我需要将该数据绘制成合适的图表，请你自行选择最适合的图表类型进行绘画。
先理解用户的要求和这个查询的结果数据，说出你的思路，以及他适合什么样的图表。最后给我绘制用的Python代码。
图表中不出现中文，文本全使用英文。信息要尽可能详细清晰，分辨率要高。
'''
          print(prompt)
          print()
          gpt_result_3 = gpt4.call(prompt, system_prompt='你是个语言能力和逻辑理解能力很强的AI助手',
                                   print_in_stream=True)
          print()
          if '```python' not in gpt_result_3:
            yield query_result, None, '', '状态：错误 - 无图表绘制代码'
          else:
            python_code = gpt_result_3.split('```python')[1].split('```')[0].strip()
            yield query_result, None, '', '状态：执行图表绘制中...'
            
            lines = python_code.split('\n')
            lines = [line for line in lines if 'plt.savefig(' not in line]
            lines = [line for line in lines if 'plt.show(' not in line]
            python_code = '\n'.join(lines)
            
            python_code = f'''
from io import BytesIO
{python_code}

# 使用 BytesIO 保存图像数据
buf = BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)
plt.close()
buf
'''
            print('Execute Python Code...')
            print(python_code)
            print()
            
            try:
              local_vars = {}
              exec(python_code, {}, local_vars)
              image_data = local_vars['buf']  # 从字典中提取图像数据
              pil_image = Image.open(image_data)
              print('Table Generate Success.')
              print('')
              
              yield query_result, pil_image, '', '状态：正在给出总结...'
              prompt = f'''
用户提出了以下要求：
{text}

程序在数据库中搜索到了该问题的对应信息结果：
{query_result}

并且我已经将数据展示在了上方，并绘制了图表去进一步可视化展示数据。

现在请你和用户总结一下这个问题的回答，例如 “从上面的结果我们可以看出...” “综上所述...” 等。
回答要正式，我会直接把你回答的话给用户看，所以不要回复我，只需要跟用户说话。
'''
              finally_gpt_result_4 = ''
              for gpt_result_4 in gpt4.call_generator(prompt, '你是个语言能力和逻辑理解能力很强的AI助手', True):
                finally_gpt_result_4 = gpt_result_4
                yield query_result, pil_image, gpt_result_4, '状态：正在给出总结...'
              print()
              print('\nFinished.\n')
              yield query_result, pil_image, finally_gpt_result_4, '状态：完成'
            except Exception as e:
              yield query_result, None, '', '状态：错误 - 图像绘制执行失败'
              print('Execute Python Code Error.', e)