# K-Read Coach 架构文档

## 项目概述

K-Read Coach 是一款韩语朗读练习工具，用户选择特定话题和句子，上传自己的朗读音频，系统通过语音识别转录音频内容，与标准文本进行相似度比较，并生成个性化反馈帮助用户改进发音。

## 文件结构

```
K-Read-Coach/
├── app.py                          # Streamlit 主应用程序入口
├── requirements.txt                # Python 依赖包列表
├── modules/
│   ├── __init__.py                 # 模块包初始化文件
│   ├── data_loader.py              # 数据集加载与话题/句子管理模块
│   ├── asr_interface.py            # 语音识别转录接口层（可插拔设计）
│   ├── comparison.py               # 文本相似度比较计算模块
│   └── feedback.py                 # 基于相似度生成反馈模块
├── data/                           # 数据目录（可选）
│   ├── k_read_coach_dataset.csv    # 真实数据集（话题、句子、参考音频等）
│   └── clips/                      # 参考音频文件存储目录
├── uploads/                        # 用户上传音频临时存储目录
└── docs/                           # 项目文档目录
    └── architecture.md             # 本文件：架构设计文档
```

## 模块职责

### data_loader.py
**职责**：加载并管理数据集，提供话题分类和句子查询功能。

**接口签名**：
```python
load_dataset(csv_path: str) -> (DataFrame, bool)
    # 加载 CSV 数据集，返回 DataFrame 和是否成功标志
    # 当 CSV 不存在时返回 mock 数据集

get_categories(df) -> list[str]
    # 提取数据集中所有话题分类

get_sentences_by_category(df, category) -> DataFrame
    # 根据话题分类返回对应的句子列表
```

### asr_interface.py
**职责**：抽象语音识别转录接口，提供统一的 ASR 调用接口。

**接口签名**：
```python
transcribe_audio(audio_path: str) -> str
    # 对上传的音频文件进行转录
    # 当前实现为 mock，固定返回 "안녕하세요"
```

### comparison.py
**职责**：计算用户朗读文本与标准文本之间的相似度。

**接口签名**：
```python
compare_texts(target: str, recognized: str) -> dict
    # 比较目标文本和识别文本，返回结构：
    # {"target": str, "recognized": str, "score": float}
    # score 范围 [0.0, 1.0]，值越高表示相似度越高
```

### feedback.py
**职责**：基于相似度分数生成用户反馈。

**接口签名**：
```python
generate_feedback(score: float) -> str
    # 根据相似度分数生成反馈文本
    # 返回针对性的改进建议
```

## ASR 接口设计说明

ASR 功能被独立抽象为 `asr_interface.py` 模块，而不是直接在 `app.py` 中调用第三方 ASR 库。这样设计的好处包括：
- **易于替换**：当需要集成真实 ASR 服务（如 Google Speech-to-Text、OpenAI Whisper 等）时，只需修改 `transcribe_audio()` 函数的实现，无需改动应用层代码。
- **解耦应用逻辑**：应用层与具体 ASR 提供商无关，降低耦合度。
- **便于测试**：可轻松用 mock 实现进行单元测试，无需依赖外部 API。

替换步骤：在 `asr_interface.py` 中导入真实 ASR SDK（如 `from google.cloud import speech_v1`），在 `transcribe_audio()` 函数内调用其 API，返回转录结果字符串即可。

## 数据流

```
load_dataset
    ↓
    用户在 Streamlit UI 上选择话题
    ↓
    根据话题获取句子列表
    ↓
    用户选择要朗读的句子
    ↓
    用户上传朗读音频文件
    ↓
transcribe_audio
    ↓
    获得用户朗读的转录文本
    ↓
compare_texts
    ↓
    获得相似度分数 (0.0~1.0)
    ↓
generate_feedback
    ↓
    生成个性化反馈文本
    ↓
    在 UI 上显示相似度分数和反馈建议
```

**流程说明**：
1. **load_dataset** — 应用启动时加载话题和句子数据，为用户提供选择范围。
2. **话题与句子选择** — 用户通过 Streamlit 选择框级联选择话题和对应句子。
3. **音频上传** — 用户上传自己的朗读音频文件到 `uploads/` 目录。
4. **transcribe_audio** — 调用 ASR 模块将音频转录为文本。
5. **compare_texts** — 比较转录文本与标准句子文本，计算相似度分数。
6. **generate_feedback** — 根据相似度分数生成针对性的反馈和改进建议。
7. **显示结果** — 在 Streamlit UI 上展示相似度分数、转录文本对比和反馈建议。
