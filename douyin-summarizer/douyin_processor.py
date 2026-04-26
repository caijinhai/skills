#!/usr/bin/env python3
"""
抖音无水印视频下载和文案提取工具

功能:
1. 从抖音分享链接获取无水印视频下载链接
2. 下载视频并提取音频
3. 使用本地语音转文本从音频中提取文本
4. 自动保存文案到文件

使用示例:
  python douyin_processor.py --link "抖音分享链接"
  python douyin_processor.py --link "抖音分享链接" --output ./output
"""

import os
import re
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime


def check_dependencies():
    """检查必要的依赖是否已安装"""
    missing = []
    try:
        import requests
    except ImportError:
        missing.append("requests")
    try:
        import ffmpeg
    except ImportError:
        missing.append("ffmpeg-python")

    if missing:
        print(f"缺少依赖：{', '.join(missing)}")
        print(f"请运行：pip install {' '.join(missing)}")
        sys.exit(1)


check_dependencies()

import requests
import ffmpeg

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1'
}


class DouyinProcessor:
    """抖音视频处理器"""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir) if output_dir else Path("./douyin-output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def parse_share_url(self, share_text: str) -> dict:
        """从分享文本中提取无水印视频链接"""
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', share_text)
        if not urls:
            raise ValueError("未找到有效的分享链接")

        share_url = urls[0]
        
        if 'v.douyin.com' in share_url:
            share_response = requests.get(share_url, headers=HEADERS, allow_redirects=True)
            video_id = share_response.url.split("?")[0].strip("/").split("/")[-1]
            share_url = f'https://www.iesdouyin.com/share/video/{video_id}'
        else:
            video_id_match = re.search(r'video/(\d+)', share_url)
            if video_id_match:
                video_id = video_id_match.group(1)
                share_url = f'https://www.iesdouyin.com/share/video/{video_id}'

        response = requests.get(share_url, headers=HEADERS)
        response.raise_for_status()

        pattern = re.compile(
            pattern=r"window\._ROUTER_DATA\s*=\s*(.*?)</script>",
            flags=re.DOTALL,
        )
        find_res = pattern.search(response.text)

        if not find_res or not find_res.group(1):
            raise ValueError("从 HTML 中解析视频信息失败")

        json_data = json.loads(find_res.group(1).strip())
        VIDEO_ID_PAGE_KEY = "video_(id)/page"
        NOTE_ID_PAGE_KEY = "note_(id)/page"

        if VIDEO_ID_PAGE_KEY in json_data["loaderData"]:
            original_video_info = json_data["loaderData"][VIDEO_ID_PAGE_KEY]["videoInfoRes"]
        elif NOTE_ID_PAGE_KEY in json_data["loaderData"]:
            original_video_info = json_data["loaderData"][NOTE_ID_PAGE_KEY]["videoInfoRes"]
        else:
            raise Exception("无法从 JSON 中解析视频或图集信息")

        data = original_video_info["item_list"][0]

        video_url = data["video"]["play_addr"]["url_list"][0].replace("playwm", "play")
        desc = data.get("desc", "").strip() or f"douyin_{data.get('aweme_id', 'unknown')}"
        desc = re.sub(r'[\\/:*?"<>|]', '_', desc)

        return {
            "url": video_url,
            "title": desc,
            "video_id": data.get("aweme_id", "unknown"),
            "author": data.get("author", {}).get("nickname", "unknown")
        }

    def download_video(self, video_info: dict, show_progress: bool = True) -> Path:
        """下载视频"""
        filename = f"{video_info['video_id']}.mp4"
        filepath = self.output_dir / filename

        if show_progress:
            print(f"正在下载视频：{video_info['title']}")

        response = requests.get(video_info['url'], headers=HEADERS, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        downloaded = 0
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if show_progress and total_size > 0:
                        progress = downloaded / total_size * 100
                        print(f"\r下载进度：{progress:.1f}%", end="", flush=True)

        if show_progress:
            print(f"\n视频下载完成：{filepath}")
        return filepath

    def extract_audio(self, video_path: Path, show_progress: bool = True) -> Path:
        """从视频文件中提取音频"""
        audio_path = video_path.with_suffix('.mp3')

        if show_progress:
            print("正在提取音频...")
        try:
            (
                ffmpeg
                .input(str(video_path))
                .output(str(audio_path), acodec='libmp3lame', q=0)
                .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            )
            if show_progress:
                print(f"音频提取完成：{audio_path}")
            return audio_path
        except Exception as e:
            raise Exception(f"提取音频时出错：{str(e)}")

    def transcribe_audio(self, audio_path: Path, show_progress: bool = True) -> str:
        """使用本地 whisper CLI 转录音频"""
        if show_progress:
            print("正在调用 whisper 进行语音识别...")
        
        try:
            result = subprocess.run(
                ['whisper', str(audio_path), '--model', 'base', '--language', 'zh', '--output_format', 'txt'],
                capture_output=True,
                text=True,
                cwd=str(self.output_dir),
                timeout=600
            )
            
            txt_file = audio_path.with_suffix('.txt')
            if txt_file.exists():
                text = txt_file.read_text(encoding='utf-8')
                if show_progress:
                    print(f"语音识别完成，识别到 {len(text)} 字")
                return text
            elif result.stdout:
                return result.stdout
            elif result.stderr:
                return f"[whisper 输出：{result.stderr[:500]}]"
            else:
                return "[语音识别未产生输出]"
                
        except subprocess.TimeoutExpired:
            return "[语音转文本超时，视频可能过长]"
        except FileNotFoundError:
            return "[whisper CLI 未找到，请运行：brew install whisper]"
        except Exception as e:
            return f"[语音转文本出错：{str(e)}]"

    def generate_summary(self, text: str, video_info: dict) -> str:
        """生成总结文档"""
        summary = f"""# 抖音视频总结

## 基本信息
- **标题**: {video_info['title']}
- **作者**: {video_info['author']}
- **视频 ID**: `{video_info['video_id']}`
- **提取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 视频文案

{text}

## 关键要点

待分析...

## 总结

待生成...

---
*本文档由 douyin-summarizer 自动生成*
"""
        return summary

    def process(self, share_link: str, save_video: bool = False, show_progress: bool = True) -> dict:
        """完整处理流程"""
        result = {
            "video_info": None,
            "text": None,
            "summary_path": None,
            "video_path": None,
            "audio_path": None
        }

        try:
            if show_progress:
                print("正在解析抖音分享链接...")
            video_info = self.parse_share_url(share_link)
            result["video_info"] = video_info

            if show_progress:
                print("正在下载视频...")
            video_path = self.download_video(video_info, show_progress=show_progress)
            result["video_path"] = str(video_path)

            if show_progress:
                print("正在提取音频...")
            audio_path = self.extract_audio(video_path, show_progress=show_progress)
            result["audio_path"] = str(audio_path)

            if show_progress:
                print("正在识别语音...")
            text_content = self.transcribe_audio(audio_path, show_progress=show_progress)
            result["text"] = text_content

            if show_progress:
                print("正在生成总结文档...")
            
            video_folder = self.output_dir / video_info['video_id']
            video_folder.mkdir(parents=True, exist_ok=True)
            
            summary_path = video_folder / "summary.md"
            summary_content = self.generate_summary(text_content, video_info)
            summary_path.write_text(summary_content, encoding='utf-8')
            result["summary_path"] = str(summary_path)

            if save_video:
                saved_video_path = video_folder / f"{video_info['video_id']}.mp4"
                shutil.copy2(video_path, saved_video_path)
                result["video_path"] = str(saved_video_path)
                if show_progress:
                    print(f"视频已保存到：{saved_video_path}")

            saved_audio_path = video_folder / f"{video_info['video_id']}.mp3"
            shutil.copy2(audio_path, saved_audio_path)
            result["audio_path"] = str(saved_audio_path)

            if show_progress:
                print(f"\n✅ 处理完成！")
                print(f"总结文档：{summary_path}")
                print(f"视频目录：{video_folder}")

            if video_path.exists():
                video_path.unlink()
            if audio_path.exists() and audio_path != saved_audio_path:
                audio_path.unlink()

            return result

        except Exception as e:
            if show_progress:
                print(f"❌ 处理失败：{str(e)}")
            result["error"] = str(e)
            return result


def main():
    parser = argparse.ArgumentParser(
        description="抖音无水印视频下载和文案提取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python douyin_processor.py --link "抖音分享链接"
  python douyin_processor.py --link "抖音分享链接" --save-video
  python douyin_processor.py --link "抖音分享链接" --output ./output
        """
    )

    parser.add_argument("--link", "-l", required=True, help="抖音分享链接或包含链接的文本")
    parser.add_argument("--output", "-o", default=None, help="输出目录 (默认 ./douyin-output)")
    parser.add_argument("--save-video", "-v", action="store_true", help="同时保存视频文件")
    parser.add_argument("--quiet", "-q", action="store_true", help="安静模式，减少输出")

    args = parser.parse_args()

    output_dir = Path(args.output) if args.output else None
    processor = DouyinProcessor(output_dir)
    
    show_progress = not args.quiet
    result = processor.process(args.link, save_video=args.save_video, show_progress=show_progress)

    if not args.quiet:
        print("\n=== 处理结果 ===")
        if result.get("video_info"):
            print(f"标题：{result['video_info']['title']}")
            print(f"作者：{result['video_info']['author']}")
        if result.get("summary_path"):
            print(f"总结文档：{result['summary_path']}")
        if result.get("error"):
            print(f"错误：{result['error']}")

    print("\n" + json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
