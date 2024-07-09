import time
import pandas as pd
from io import StringIO

from structure import get_structure_info, execute_sql
from call.gpt4 import call, call_generator


# 查一下宣桥镇政府下有哪些企业
# 查查DASHENG科技有限公司在2023年每个月的累计收入变化情况
# 对比看看 DASHENG科技有限公司 和 上海联合创富实业有限公司 在2023年每个月的累计收入


prompt_template = f'''
[HISTORY]
上面是用户说的话以及历史对话内容，请你根据用户的需求解决用户的问题。

你的主要职责是帮助用户在数据库中找到对应数据，以及简单分析和绘图，你可以使用以下的工具。
1. 数据库检索工具
当回答用户问题需要从数据库中获取数据时，你可以使用数据库检索工具。你的回答中只要包含SQL语句即可，程序会自动执行SQL并将检索结果提供给你，然后你可以根据数据检索的结果继续回答。
2. 图表绘制工具
当用户询问的问题回答的数据合适绘制图表时，请主动为用户绘图。你的回答中只要包含用于绘制图表的Python代码即可，程序会自动将你的代码替换为图片。

注意事项：
1. 不要自行编造数据，所有数据请使用数据库检索工具，从数据库中查询。
2. 当且仅当你需要使用数据库检索工具时，才输出SQL语句，否则不要输出SQL语句。当且仅当你需要使用图表绘制工具时，才输出Python代码，否则不要输出Python代码。
3. 当使用数据库检索工具时，请尽量使用少的表来解决问题，有时会需要用到多个表，有时只需一个表，请你自行判断。
4. 当使用数据库检索工具时，用户提问内容包含公司名时，公司名可能与数据库中无法完全匹配，请使用模糊匹配。例如用户说“创富公司”，要能匹配到“上海联合创富实业有限公司”，你可以使用“xxx LIKE '%创富%' AND xxx LIKE '%公司'”这样的形式。
4. 用户看不到SQL运行的结果，你可以以表格形式将数据告诉用户。如果数据很简单，你也可以将结果直接加进你回答的文本中。
5. 请自行判断合适的图表类型，如折线图、柱状图、热力图等等。数据不适合绘制图表时，请不要输出Python代码。
6. 图像尺寸要大，至少达到figsize=(13, 8)。
7. 当你将绘图代码输出后，程序会立即完成绘图，并用图片替换文中的Python代码。不用提示用户等待，不用提示用户去执行代码。你只要对着图片进行简单介绍，并总结即可。

下方是表结构，当你需要使用数据库检索工具时，请参考表结构以输出更准确的SQL语句。
[STRUCTURE]
'''


python_template = f'''
from io import BytesIO
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']   # 使用微软雅黑
plt.rcParams['axes.unicode_minus'] = False   # 解决负号显示为方块的问题

[CODE]

plt.savefig('[FILENAME]', format='png')  # 替换显示为保存到指定路径
'''


def get_history_text(history, query_result):
  history_text = ''
  for x in history:
    if x[0] is not None:
      if isinstance(x[0], str):
        if len(x[0]) > 0:
          history_text += 'User:\n' + x[0] + '\n\n'
      else:
        history_text += 'User:\n[IMAGE]' + '\n\n'
    if x[1] is not None:
      if isinstance(x[1], str):
        if len(x[1]) > 0:
          history_text += 'Assistant:\n' + x[1] + '\n\n'
      else:
        history_text += 'Assistant:\n[IMAGE]' + '\n\n'
  if query_result:
    history_text += 'System:\n' + query_result + '\n\n'
  return history_text


def inference(history):
  query_result = ''
  while True:
    history_text = get_history_text(history, query_result)
    if query_result:
      query_result = ''
    print(history_text, '\n')
    structure = get_structure_info()
    prompt = prompt_template.replace('[HISTORY]', history_text)
    print(prompt, '\n')
    prompt = prompt.replace('[STRUCTURE]', structure)
    history.append([None, ''])
    for result in call_generator(prompt, print_in_stream=True):
      history[-1][1] = result
      yield history
      if '```sql' in result and '```' in result.split('```sql')[1]:
        break
    print('\n')
    
    last_result = history[-1][1]
    if '```sql' in last_result:
      sql_query = last_result.split('```sql')[1].split('```')[0].strip()
      print(f'SQL:\n{sql_query}\n')
      query_result = execute_sql(sql_query)
      
      # 处理SQL成Markdown表格
      data = query_result.strip()
      lines = data.split('\n')
      processed_lines = [','.join(line.split()) for line in lines]
      processed_data = '\n'.join(processed_lines)
      df = pd.read_csv(StringIO(processed_data))
      markdown_table = df.to_markdown(index=True)
      
      history.append([None, 'SQL Query Result:\n\n' + markdown_table])
      yield history
      print(f'Query Result:\n{query_result}')
      
    if '```python' in last_result:
      python_code = last_result.split('```python')[1].split('```')[0].strip()
      lines = []
      pass_line_keys = ['plt.savefig(', 'plt.show(', 'import matplotlib.pyplot as']
      for line in python_code.split('\n'):
        if not any([key in line for key in pass_line_keys]):
          lines.append(line)
      python_code = '\n'.join(lines)
      filename = f'./output/{int(time.time() * 10000000)}.png'
      python_code = python_template.replace('[CODE]', python_code).replace('[FILENAME]', filename)
      print('Execute Python Code...\n')
      print(python_code, '\n')
      
      try:
        exec(python_code)
        pos = last_result.rfind('```') + 3
        history[-1][1] = last_result[:pos]
        history.append([None, (filename, 'output.png')])
        last_result = last_result[pos:]
        if last_result:
          history.append([None, last_result])
        yield history
        print('Table Generate Success.')
      except Exception as e:
          print('Execute Python Code Error.', e)
      
    if not query_result:
      break
  

if __name__ == '__main__':
  inference([['查查 DASHENG科技有限公司 在2023年每个月的累计收入变化情况', None]])
  
