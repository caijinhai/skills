#!/usr/bin/env python3
"""
发送语音消息到飞书 - IndexTTS2 版本
参考 tts-pocket 的实现
依赖：ffmpeg, requests
"""
import os
import subprocess
import requests
import json
import sys
import tempfile

# ============= 配置 =============
# 飞书 Bot 凭证
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")

# 代理设置
PROXY = {}  # 如果需要代理 {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}

# IndexTTS2 配置
MODEL_DIR = os.path.expanduser("~/miniconda3/envs/indextts2/checkpoints")
SKILL_DIR = os.path.expanduser("~/Documents/skills/tts-indextts2")
CONDA_ENV = "indextts2_fixed"

# ============= 飞书 API =============
def get_feishu_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }, proxies=PROXY)
    data = resp.json()
    if "tenant_access_token" not in data:
        print(f"❌ 获取 token 失败：{data}")
        sys.exit(1)
    return data["tenant_access_token"]

def create_reference_audio(emotion="neutral"):
    """创建参考音频"""
    temp_dir = tempfile.mkdtemp()
    
    # 根据情绪选择参考文本
    emotion_texts = {
        "happy": "太棒了！今天真是美好的一天！",
        "calm": "你好，这是参考音频。",
        "sad": "唉，今天心情不太好。",
        "excited": "哇！太令人兴奋了！",
        "neutral": "你好，这是参考音频。"
    }
    
    ref_text = emotion_texts.get(emotion, emotion_texts["neutral"])
    ref_m4a = os.path.join(temp_dir, "ref.m4a")
    ref_wav = os.path.join(temp_dir, "ref.wav")
    
    # 使用 say 命令生成参考音频
    subprocess.run([
        "say", "-v", "Ting-Ting", "-o", ref_m4a, ref_text
    ], check=True, capture_output=True)
    
    # 转换为 24kHz WAV
    subprocess.run([
        "ffmpeg", "-i", ref_m4a, "-ar", "24000", "-y", ref_wav
    ], check=True, capture_output=True)
    
    os.remove(ref_m4a)
    return ref_wav

def generate_speech(text, ref_audio=None):
    """使用 IndexTTS2 生成语音"""
    sys.path.insert(0, os.path.join(SKILL_DIR, "index-tts"))
    
    from indextts.infer import IndexTTS
    
    output_path = os.path.join(SKILL_DIR, "output_voice.wav")
    
    # 如果没有参考音频，创建默认的
    if ref_audio is None:
        ref_audio = os.path.join(SKILL_DIR, "test_macos.wav")
        if not os.path.exists(ref_audio):
            print("⚠️  未找到参考音频，创建默认参考...")
            ref_audio = create_reference_audio("neutral")
    
    print(f"🎤 使用 IndexTTS2 生成语音...")
    print(f"   文本：{text[:50]}...")
    print(f"   参考：{ref_audio}")
    
    try:
        tts = IndexTTS(
            cfg_path=os.path.join(MODEL_DIR, "config.yaml"),
            model_dir=MODEL_DIR,
            is_fp16=False,
            device="cpu",
            use_cuda_kernel=False
        )
        
        tts.infer(
            text=text,
            audio_prompt=ref_audio,
            output_path=output_path,
            verbose=False
        )
        
        print(f"✅ 语音生成成功：{output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ 生成失败：{e}")
        print("⚠️  回退到 macOS say...")
        return generate_with_say(text)

def generate_with_say(text):
    """使用 macOS say 生成语音（备用方案）"""
    m4a_path = os.path.join(SKILL_DIR, "output_voice.m4a")
    subprocess.run([
        "say", "-v", "Ting-Ting", "-o", m4a_path, text
    ], check=True, capture_output=True)
    
    # 转换为 WAV
    wav_path = os.path.join(SKILL_DIR, "output_voice.wav")
    subprocess.run([
        "ffmpeg", "-i", m4a_path, "-ar", "24000", "-y", wav_path
    ], check=True, capture_output=True)
    
    os.remove(m4a_path)
    print(f"✅ 语音生成成功（macOS say）：{wav_path}")
    return wav_path

def wav_to_opus(wav_path):
    """将 WAV 转换为 OPUS 格式（参照 tts-pocket）"""
    opus_path = wav_path.replace(".wav", ".opus")
    
    # 参照 tts-pocket 使用 24k bitrate
    subprocess.run([
        "ffmpeg", "-i", wav_path,
        "-c:a", "libopus",
        "-b:a", "24k",
        "-y", opus_path
    ], check=True, capture_output=True)
    
    print(f"✅ OPUS 转换完成：{opus_path}")
    return opus_path

def upload_feishu_file(token, opus_path):
    """上传 OPUS 文件到飞书，返回 file_key（参照 tts-pocket）"""
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(opus_path, "rb") as f:
        files = {"file": f}
        data = {
            "file_type": "opus",  # 关键：使用 opus 类型
            "name": os.path.basename(opus_path)
        }
        resp = requests.post(url, headers=headers, files=files, data=data, proxies=PROXY)
    
    result = resp.json()
    print(f"上传结果：{result}")
    
    if "data" not in result or "file_key" not in result.get("data", {}):
        print(f"❌ 上传失败：{result}")
        return None
    
    return result["data"]["file_key"]

def send_feishu_voice(token, receive_id, file_key):
    """发送语音消息（参照 tts-pocket）"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "receive_id": receive_id,
        "msg_type": "audio",
        "content": json.dumps({"file_key": file_key})
    }
    resp = requests.post(url, headers=headers, json=payload, proxies=PROXY)
    result = resp.json()
    print(f"发送结果：{result}")
    return result

# ============= 主函数 =============
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="IndexTTS2 飞书语音发送")
    parser.add_argument("text", help="要转换的文本")
    parser.add_argument("receive_id", help="接收者 ID (open_id)")
    parser.add_argument("--happy", action="store_true", help="快乐情绪")
    parser.add_argument("--calm", action="store_true", help="平静情绪")
    parser.add_argument("--sad", action="store_true", help="悲伤情绪")
    parser.add_argument("--excited", action="store_true", help="兴奋情绪")
    parser.add_argument("--ref", help="参考音频路径")
    
    args = parser.parse_args()
    
    # 确定情绪
    emotion = "neutral"
    if args.happy:
        emotion = "happy"
    elif args.calm:
        emotion = "calm"
    elif args.sad:
        emotion = "sad"
    elif args.excited:
        emotion = "excited"
    
    print("=" * 50)
    print("🎤 IndexTTS2 飞书语音发送（参照 tts-pocket）")
    print("=" * 50)
    print(f"📝 文本：{args.text}")
    print(f"👤 接收者：{args.receive_id}")
    print(f"😊 情绪：{emotion}")
    print("")
    
    # 创建参考音频
    if args.ref:
        ref_audio = args.ref
    else:
        print(f"🎵 创建 {emotion} 情绪参考音频...")
        ref_audio = create_reference_audio(emotion)
    
    # 生成语音
    wav_path = generate_speech(args.text, ref_audio)
    if not wav_path:
        sys.exit(1)
    
    # 转换为 OPUS
    print("🔄 转换为 OPUS 格式...")
    opus_path = wav_to_opus(wav_path)
    
    # 获取飞书 token
    print("📱 获取飞书 token...")
    token = get_feishu_token()
    
    # 上传到飞书
    print("⬆️  上传到飞书...")
    file_key = upload_feishu_file(token, opus_path)
    if not file_key:
        sys.exit(1)
    
    # 发送语音消息
    print("📤 发送语音消息...")
    result = send_feishu_voice(token, args.receive_id, file_key)
    
    # 清理临时文件
    for path in [opus_path, wav_path]:
        if os.path.exists(path):
            os.remove(path)
    
    # 显示结果
    print("")
    if result.get("code", 1) == 0 or "data" in result:
        print("✅ 发送成功！")
        print(f"   消息 ID: {result.get('data', {}).get('message_id', 'N/A')}")
    else:
        print(f"❌ 发送失败：{result}")
        sys.exit(1)

if __name__ == "__main__":
    main()
