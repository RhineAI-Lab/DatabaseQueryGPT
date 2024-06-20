from moviepy.editor import TextClip, CompositeVideoClip, concatenate_videoclips
from datetime import timedelta, datetime

# 初始化时间和一个空列表来存放片段
start_time = timedelta(seconds=0)
end_time = timedelta(minutes=70)
time_diff = end_time - start_time
clips = []

# 当前时间初始化为开始时间
current_time = start_time

# 循环直到达到结束时间
while current_time <= end_time:
  # 格式化当前时间为时分秒字符串
  time_str = str(current_time).split('.')[0]  # 去掉毫秒部分
  print(time_str)
  # 创建TextClip
  text_clip = TextClip(time_str, fontsize=400, color='white', font='Microsoft YaHei')
  text_clip = text_clip.set_position(('center', 'center')).set_duration(0.25)
  clips.append(text_clip)
  
  # 每次循环递增1秒
  current_time += timedelta(seconds=1)

# 将所有片段连接起来
final_clip = concatenate_videoclips(clips)

# 设置视频背景为黑色
final_clip = final_clip.on_color(size=(1792, 828), color=(0, 0, 0))

# 导出视频
final_clip.write_videofile("countup_70minutes.mp4", fps=24)
