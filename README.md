# VoiceAI - 智能语音对话系统

<div align="center">
    <img src="https://img.shields.io/badge/项目-比赛作品-blue?style=for-the-badge" alt="比赛项目" height="20">
    <img src="https://img.shields.io/badge/技术-语音AI-green?style=for-the-badge" alt="AI语音对话" height="20">
    <img src="https://img.shields.io/badge/框架-Python%20%7C%20FastAPI%20%7C%20Whisper-orange?style=for-the-badge" alt="技术栈" height="20">
    <img src="https://img.shields.io/badge/状态-可用-brightgreen?style=for-the-badge" alt="状态" height="20">
</div>

<br/>

<div align="center">
    <h2>一个可以语音聊天的AI角色系统</h2>
    <p>authorized by 云起技术团</p>
</div>

<br/>

## 🎬 项目演示视频

<div align="center">
    <a href="https://www.bilibili.com/video/BV1HnnfziETE/?share_source=copy_web&vd_source=6bde61bba0fd3c0a0d70b8c2c6074bbe" target="_blank">
        <img src="https://img.shields.io/badge/📺-观看演示视频-red?style=for-the-badge&logo=bilibili" alt="观看演示视频" height="40">
    </a>
    <p><strong>【完整项目展示】</strong></p>
    <p><em>点击上方按钮观看完整项目演示视频</em></p>
</div>

<br/>




## 1. 目标用户分析

**你计划将这个网页面向什么类型的用户？这些类型的用户他们面临什么样的痛点，你设想的用户故事是什么样呢？**

这个系统主要面向四类用户：首先是AI技术爱好者和开发者，他们面临ChatGPT太贵（一个月140块）和商业平台限制太多的问题，希望能有一个便宜且可定制的语音对话系统来学习AI技术；其次是教育工作者和学习者，他们缺少生动有趣的AI教学工具，希望让学生与历史人物对话来学习，比如与苏格拉底讨论哲学；第三是内容创作者，他们需要新颖的AI交互内容，想要与AI角色对话来制作有趣的内容；最后是普通用户，他们想要更好的中文支持，希望能有一个能听懂中文的AI助手来聊天和解决问题。

## 2. 功能需求分析

**你认为这个网页需要哪些功能？这些功能各自的优先级是什么？你计划本次开发哪些功能？**

这个系统需要实现语音对话、角色扮演、Web界面等核心功能，其中语音对话和角色扮演是最高优先级，已经完成。接下来计划实现知识问答、情感分析、多轮对话等重要功能，让AI能回答专业问题、识别用户情绪、提供更好的上下文理解。未来还会考虑任务执行、内容创作、个性化等增强功能。本次开发重点是系统稳定性优化、用户体验提升和功能测试完善。

## 3. LLM模型选择

**你计划采纳哪家公司的哪个 LLM 模型能力？你对比了哪些，你为什么选择用该 LLM 模型？**

我对比了GPT-4、GPT-3.5、Claude-3和DeepSeek几个主流模型，最终选择了DeepSeek。主要原因是GPT-4太贵了用不起，GPT-3.5还是有点贵，Claude-3需要改代码比较麻烦，而DeepSeek价格便宜、中文支持很好、完全兼容OpenAI API不用改代码。实际测试下来，DeepSeek的中文理解准确率达到95%+，角色扮演能力优秀，响应时间小于2秒，服务可用性99%+。对于语音识别，我选择了Whisper，因为它开源免费、识别准确率高特别是中文、可以本地部署保证数据安全、支持多种音频格式。

## 4. AI角色技能扩展

**你期望 AI 角色除了语音聊天外还应该有哪些技能？**

除了基础的语音对话和角色扮演，AI角色还应该具备知识问答能力，能够回答各角色领域的专业问题、集成网络搜索获取最新信息、支持多语言翻译和学习辅导；情感交互能力，能够识别用户情绪状态、根据用户情绪调整回复风格、提供心理支持和个性化关怀；任务执行能力，帮助用户安排日程、整理信息、提供决策支持、协助项目管理；创意协作能力，协助写作设计编程、提供创意灵感、协助代码调试、支持艺术创作；教育指导能力，根据用户水平定制教学内容、提供技能培训、评估学习进度、构建个性化知识体系。这些技能按优先级分为知识问答（近期实现）、情感交互（中期规划）、任务执行和创意协作（长期规划）、教育指导（未来愿景）。

## 技术实现

### 已经做好的功能
- **语音对话**: 说话转文字，AI回复转语音
- **角色扮演**: 可以跟马斯克、苏格拉底、哈利波特等角色聊天
- **Web界面**: 基于Next.js的现代化界面
- **音频处理**: 解决了立体声转单声道的问题（这个坑踩了好久）
- **内存优化**: 限制音频长度，避免内存溢出

### 解决的技术问题
1. **立体声崩溃问题**: 前端传过来的音频是立体声，Whisper只支持单声道，直接传会崩溃
2. **内存溢出**: 长音频会导致内存不足，现在限制在2秒内
3. **WebSocket连接**: 处理音频流传输，确保实时性
4. **模型兼容**: DeepSeek完全兼容OpenAI API，无缝切换

## 技术架构

**后端**: FastAPI + WebSocket + Whisper Medium + DeepSeek API + Edge TTS + ChromaDB  
**前端**: Next.js + React + WebRTC + 现代化响应式设计

### 主要技术栈
- **语音识别**: Whisper Medium（本地部署）
- **大语言模型**: DeepSeek API（便宜又好用）
- **语音合成**: Edge TTS（微软的免费TTS）
- **向量数据库**: ChromaDB（存储对话历史）
- **后端框架**: FastAPI（异步处理）
- **前端框架**: Next.js（React生态）

## 快速开始

```bash
# 1. 克隆项目
git clone <your-repo-url> && cd RealChar

# 2. 安装依赖
conda create -n aichat python=3.11
conda activate aichat
    pip install -r requirements.txt

# 3. 配置环境变量
    cp .env.example .env
# 编辑 .env 文件，配置 API 密钥

# 4. 启动服务
python cli.py run-uvicorn  # 后端
cd client/next-web && npm install && npm run dev  # 前端

# 5. 访问应用
# 浏览器打开: http://localhost:3000
```

## 支持的角色

**知名人物**: 马斯克、苏格拉底、乔布斯、奥特曼  
**虚构角色**: 哈利·波特、雷神、圣诞老人

## 性能指标

- **识别精度**: 95%+ (Whisper Medium)
- **响应时间**: <2秒
- **内存使用**: <2GB
- **支持语言**: 中英文混合

## 许可证

MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

<div align="center">
    <h3>🎉 体验智能语音对话，开启AI角色扮演新纪元！ 🎉</h3>
</div>