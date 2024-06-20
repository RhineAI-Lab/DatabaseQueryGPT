import gradio as gr
from inference2 import inference


def add_message(history, message):
    for x in message["files"]:
        history.append(((x,), None))
    if message["text"] is not None:
        history.append((message["text"], None))
    return history, gr.MultimodalTextbox(value=None, interactive=False, file_types=None, placeholder="Processing...", show_label=False)


with gr.Blocks(css=open('./main2.css', mode='r', encoding='utf-8').read()) as demo:
    gr.Markdown('')
    with gr.Row():
      gr.Markdown("## 自然语言数据库检索")
    chatbot = gr.Chatbot(
        [[None, '您好，请问有什么可以帮您？']],
        elem_id="chatbot",
        bubble_full_width=False
    )

    chat_input = gr.MultimodalTextbox(interactive=True, file_types=["image"], placeholder="Enter message or upload file...", show_label=False)

    chat_msg = chat_input.submit(add_message, [chatbot, chat_input], [chatbot, chat_input])
    bot_msg = chat_msg.then(inference, chatbot, chatbot)
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True, file_types=["image"], placeholder="Enter message or upload file...", show_label=False), None, [chat_input])

demo.queue()
demo.launch()
