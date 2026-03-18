#!/usr/bin/env python3
"""
IndexTTS2 语音合成脚本
将文本转换为语音
"""

import os
import sys
import wave
import numpy as np
import argparse

def create_placeholder_audio(text, output_path, duration=3):
    """
    创建占位符音频（当模型不可用时）
    生成一个简单的正弦波
    """
    sample_rate = 16000
    frequency = 440  # A4 note
    
    # 根据文本长度调整持续时间
    text_length = len(text)
    duration = min(max(text_length * 0.3, 2), 10)  # 2-10 秒
    
    # 生成音频数据
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # 添加淡入淡出
    fade_length = int(0.1 * sample_rate)
    fade_in = np.linspace(0, 1, fade_length)
    fade_out = np.linspace(1, 0, fade_length)
    audio_data[:fade_length] *= fade_in
    audio_data[-fade_length:] *= fade_out
    
    # 保存为 WAV 文件
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
        wav_file.writeframes(audio_bytes)
    
    return output_path

def synthesize_with_indextts2(text, output_path, voice=None):
    """
    使用 IndexTTS2 模型合成语音
    """
    try:
        from indextts2 import IndexTTS2
        
        model_dir = os.path.expanduser("~/miniconda3/envs/indextts2/models")
        tts = IndexTTS2(model_path=model_dir, voice=voice)
        tts.synthesize(text, output_path=output_path)
        return True
        
    except Exception as e:
        print(f"⚠️  IndexTTS2 合成失败：{e}")
        return False

def synthesize_with_piper(text, output_path, voice=None):
    """
    使用 Piper TTS 作为备选方案
    Piper 是一个快速的本地 TTS 引擎
    """
    try:
        from piper import PiperVoice
        
        # Piper 模型路径
        model_dir = os.path.expanduser("~/miniconda3/envs/indextts2/models/piper")
        model_path = os.path.join(model_dir, "zh_CN-medium.onnx")
        config_path = os.path.join(model_dir, "zh_CN-medium.onnx.json")
        
        if not os.path.exists(model_path):
            print("⚠️  Piper 模型不存在")
            return False
        
        voice = PiperVoice.load(model_path, config_path=config_path)
        
        with wave.open(output_path, 'wb') as wav_file:
            voice.synthesize(text, wav_file)
        
        return True
        
    except Exception as e:
        print(f"⚠️  Piper 合成失败：{e}")
        return False

def synthesize_with_espeak(text, output_path):
    """
    使用 eSpeak 作为备选方案
    """
    try:
        import subprocess
        
        # 使用 eSpeak 生成 WAV
        subprocess.run([
            'espeak', '-v', 'zh',
            '-w', output_path,
            text
        ], check=True)
        
        return True
        
    except Exception as e:
        print(f"⚠️  eSpeak 合成失败：{e}")
        return False

def synthesize_with_macos_say(text, output_path):
    """
    使用 macOS say 命令作为备选方案
    """
    try:
        import subprocess
        
        # 使用 say 生成 M4A，然后转换（如果需要 WAV）
        temp_m4a = output_path.replace('.wav', '.m4a')
        
        subprocess.run([
            'say', '-o', temp_m4a,
            '-v', 'Ting-Ting',
            text
        ], check=True)
        
        # 如果需要 WAV 格式，尝试转换
        if output_path.endswith('.wav'):
            try:
                subprocess.run([
                    'ffmpeg', '-i', temp_m4a, '-y',
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',
                    output_path
                ], check=True, capture_output=True)
                os.remove(temp_m4a)
            except:
                # 如果没有 ffmpeg，重命名 M4A
                os.rename(temp_m4a, output_path)
        
        return True
        
    except Exception as e:
        print(f"⚠️  macOS say 合成失败：{e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='IndexTTS2 语音合成')
    parser.add_argument('text', help='要转换的文本')
    parser.add_argument('output', help='输出文件路径')
    parser.add_argument('-v', '--voice', default=None, help='语音类型')
    
    args = parser.parse_args()
    
    print(f"📝 文本：{args.text}")
    print(f"📁 输出：{args.output}")
    print("")
    
    # 尝试不同的 TTS 引擎
    engines = [
        ("IndexTTS2", lambda: synthesize_with_indextts2(args.text, args.output, args.voice)),
        ("Piper", lambda: synthesize_with_piper(args.text, args.output, args.voice)),
        ("eSpeak", lambda: synthesize_with_espeak(args.text, args.output)),
        ("macOS say", lambda: synthesize_with_macos_say(args.text, args.output)),
    ]
    
    for engine_name, engine_func in engines:
        print(f"🔄 尝试使用 {engine_name}...")
        if engine_func():
            print(f"✅ {engine_name} 合成成功！")
            return 0
        else:
            print(f"   {engine_name} 不可用")
    
    # 如果所有引擎都失败，使用占位符
    print("⚠️  所有 TTS 引擎都不可用，生成占位符音频...")
    create_placeholder_audio(args.text, args.output)
    print("✅ 占位符音频已生成")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
