/**
 * 抖音链接文案抓取总结技能
 * 
 * 功能：
 * 1. 解析抖音分享链接
 * 2. 下载无水印视频
 * 3. 提取音频
 * 4. 语音转文本（使用本地 whisper）
 * 5. 生成结构化总结文档
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');

const execAsync = promisify(exec);

/**
 * 解析抖音链接，提取视频 ID
 * @param {string} url - 抖音分享链接
 * @returns {string|null} 视频 ID
 */
function parseDouyinUrl(url) {
  const patterns = [
    /video\/(\d+)/,
    /v\.douyin\.com\/([^\/]+)/,
    /douyin\.com\/([^\/\?]+)/,
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) {
      return match[1];
    }
  }
  return null;
}

/**
 * 调用 Python 脚本处理抖音链接
 * @param {string} douyinUrl - 抖音链接
 * @param {boolean} saveVideo - 是否保存视频
 * @param {string} outputDir - 输出目录
 * @returns {Promise<object>} 处理结果
 */
async function processDouyinLink(douyinUrl, saveVideo = false, outputDir = null) {
  const scriptPath = path.join(__dirname, 'douyin_processor.py');
  
  let command = `python3 "${scriptPath}" --link "${douyinUrl}"`;
  
  if (saveVideo) {
    command += ' --save-video';
  }
  
  if (outputDir) {
    command += ` --output "${outputDir}"`;
  }
  
  try {
    const { stdout, stderr } = await execAsync(command, {
      encoding: 'utf-8',
      maxBuffer: 10 * 1024 * 1024
    });
    
    const jsonMatch = stdout.match(/\{[\s\S]*\}\s*$/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    
    throw new Error('无法解析处理结果');
  } catch (error) {
    console.error('处理失败:', error.message);
    if (error.stderr) {
      console.error('stderr:', error.stderr);
    }
    throw error;
  }
}

/**
 * 读取总结文档
 * @param {string} summaryPath - 总结文档路径
 * @returns {Promise<string>} 文档内容
 */
async function readSummary(summaryPath) {
  try {
    const content = await fs.readFile(summaryPath, 'utf-8');
    return content;
  } catch (error) {
    console.error('读取总结文档失败:', error.message);
    return null;
  }
}

/**
 * 检查依赖
 * @returns {Promise<object>} 依赖状态
 */
async function checkDependencies() {
  const deps = {
    python: false,
    requests: false,
    ffmpeg: false,
    whisper: false
  };
  
  try {
    await execAsync('python3 --version');
    deps.python = true;
  } catch (e) {}
  
  try {
    await execAsync('python3 -c "import requests"');
    deps.requests = true;
  } catch (e) {}
  
  try {
    await execAsync('ffmpeg -version');
    deps.ffmpeg = true;
  } catch (e) {}
  
  try {
    await execAsync('whisper --version');
    deps.whisper = true;
  } catch (e) {}
  
  return deps;
}

/**
 * 生成快速摘要（基于文案内容）
 * @param {string} text - 文案内容
 * @param {object} videoInfo - 视频信息
 * @returns {string} 摘要
 */
function generateQuickSummary(text, videoInfo) {
  const preview = text.length > 200 ? text.substring(0, 200) + '...' : text;
  
  return `
# 抖音视频快速摘要

**标题**: ${videoInfo.title}
**作者**: ${videoInfo.author}

**内容预览**:
${preview}

---
*完整文档请查看总结文件*
`.trim();
}

module.exports = {
  parseDouyinUrl,
  processDouyinLink,
  readSummary,
  checkDependencies,
  generateQuickSummary
};
