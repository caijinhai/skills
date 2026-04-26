# douyin-summarizer

抖音链接文案抓取总结技能。根据抖音分享链接自动下载视频、提取音频、语音转文本并生成总结文档。

## 激活条件
当用户提到：
- "抖音链接总结"
- "抓取抖音视频文案"
- "分析抖音视频"
- 包含 douyin.com 或 v.douyin.com 的链接

## 工作流程
1. **解析链接** - 从抖音分享链接中提取视频 ID 和无水印下载地址
2. **下载视频** - 下载无水印视频到临时目录
3. **提取音频** - 使用 ffmpeg 从视频中提取 MP3 音频
4. **语音转文本** - 调用本地 whisper 进行语音识别
5. **生成总结** - 创建 Markdown 格式的总结文档

## 依赖
- Python 3.7+
- requests
- ffmpeg-python
- ffmpeg (系统命令)
- whisper (可选，用于语音转文本)

## 安装依赖
```bash
pip install requests ffmpeg-python
# 可选：语音转文本
pip install openai-whisper
```

## 使用方式

### 在对话中使用
用户提供抖音分享链接，技能自动处理并返回总结。

```
帮我总结这个视频：https://v.douyin.com/xxxxx
```

### 命令行使用
```bash
# 完整处理
python douyin_processor.py --link "抖音分享链接"

# 保存视频
python douyin_processor.py --link "抖音分享链接" --save-video

# 指定输出目录
python douyin_processor.py --link "抖音分享链接" --output ./output
```

## 输出格式
```json
{
  "video_info": {
    "title": "视频标题",
    "author": "作者",
    "video_id": "视频 ID"
  },
  "text": "识别的文案内容",
  "summary_path": "总结文档路径",
  "video_path": "视频文件路径",
  "audio_path": "音频文件路径"
}
```

## 注意事项
1. 抖音视频需要公开可访问
2. 部分视频可能需要登录才能查看完整内容
3. 语音转文本需要安装 whisper
4. 临时文件会自动清理，最终文件保存在配置的输出目录下

## License
MIT
