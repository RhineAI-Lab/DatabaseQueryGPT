import gradio as gr

from inference import inference


def reset():
  return '', '', None, '', '状态：正常'


with gr.Blocks() as app:
  gr.Markdown('')
  with gr.Row():
    gr.Markdown("## 自然语言数据库检索")
  with gr.Row():
    gr.Markdown("在输入框中输入您的问题，点击提交，然后稍等1-2分，会得到答案。")
  with gr.Column():
    input_text = gr.Textbox("查一下 DASHENG科技有限公司 在2023年每个月的累计收入变化情况", label="请问有什么可以帮您？", lines=4, placeholder="帮我查一下...")
    with gr.Row():
      reset_button = gr.Button("重置")
      submit_button = gr.Button("提交", variant='primary')
    with gr.Row():
      status_text = gr.Markdown("状态: 正常")
    output_text = gr.Textbox(label="检索结果：", lines=6, interactive=False)
    output_image = gr.Image(label="数据图表：")
    info_text = gr.Textbox(label="大模型总结：", lines=6, interactive=False)
  
  submit_button.click(fn=inference, inputs=[input_text], outputs=[output_text, output_image, info_text, status_text])
  reset_button.click(fn=reset, outputs=[input_text, output_text, output_image, info_text, status_text])

app.launch(share=False)
