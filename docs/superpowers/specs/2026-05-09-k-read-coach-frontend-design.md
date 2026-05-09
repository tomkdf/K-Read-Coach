# K-Read Coach Streamlit 前端设计文档

## Context

K-Read Coach 是一个韩语朗读练习工具。用户选择预设句子、听参考音频、上传自己的朗读音频，系统识别后给出相似度分数和反馈。

本文档描述 `feature-streamlit-ui` 分支的前端实现计划，分三个独立上下文窗口执行：
- **窗口 1**：设计 + 规划（本文档）
- **窗口 2**：实现 `modules/` 下 4 个模块
- **窗口 3**：实现 `app.py`、`requirements.txt`、收尾

---

## 已确认的设计决策

| 问题 | 决策 |
|------|------|
| SENTENCE 下拉菜单显示内容 | 直接显示韩语句子 |
| 结果展示方式 | 简单版：识别文本 + 相似度进度条 + 一句英文反馈 |
| 音频输入方式 | 只支持文件上传（.wav / .mp3 / .m4a） |
| 界面样式 | 少量自定义 CSS，接近截图暖色调效果 |
| 架构方式 | 模块化（思路 B） |

---

## 文件结构

```
K-Read-Coach/
├── app.py                         # Streamlit 主页面
├── requirements.txt               # streamlit, pandas, rapidfuzz
│
├── data/
│   ├── k_read_coach_dataset.csv   # 真实数据（来自 develop-cleaning）
│   └── clips/
│       └── *.wav                  # 参考音频
│
├── uploads/
│   └── .gitkeep                   # 用户上传的音频保存于此
│
└── modules/
    ├── data_loader.py             # CSV 读取 + mock data fallback
    ├── asr_interface.py           # ASR 接口层（现阶段 mock）
    ├── comparison.py              # 相似度计算（rapidfuzz）
    └── feedback.py                # 根据分数生成英文反馈
```

---

## 各模块职责

### `modules/data_loader.py`
- `load_dataset(csv_path) -> (DataFrame, bool)` — 读取 CSV；不存在时返回 mock data，bool 表示是否为真实数据
- `get_categories(df) -> list` — 返回所有分类
- `get_sentences_by_category(df, category) -> DataFrame` — 按分类过滤句子
- CSV 字段：`path`, `sentence`, `english_translation`, `categories`
- Mock data 包含 Greeting / School 两个分类各一条示例句子

### `modules/asr_interface.py`
- `transcribe_audio(audio_path: str) -> str` — 唯一对外接口
- 现阶段返回固定字符串 `"안녕하세요"`（mock）
- **ASR 同学后续只需替换此函数内部实现，app.py 无需改动**

### `modules/comparison.py`
- `compare_texts(target: str, recognized: str) -> dict`
- 使用 `rapidfuzz.fuzz.ratio()` 计算相似度（项目已有此依赖）
- 返回：`{"target": str, "recognized": str, "score": float}`

### `modules/feedback.py`
- `generate_feedback(score: float) -> str`
- 分数区间：≥90 / ≥75 / ≥50 / <50，返回对应英文反馈句

---

## UI 布局

**左侧边栏：**
- 标题：K-Read Coach / Korean Read-Aloud Practice
- TOPIC 下拉菜单（来自 CSV categories）
- SENTENCE 下拉菜单（显示韩语句子，按选中 TOPIC 过滤）
- 使用 mock data 时显示黄色警告

**右侧主区域：**
- 页面标题：Practice Session
- Target sentence 卡片（韩语句子 + 英文翻译）
- Reference audio 播放器（文件不存在时显示警告）
- Your recording 文件上传区（.wav / .mp3 / .m4a）
- Analyze 按钮 + Retry 按钮
- 结果区域（Analyze 后出现）：Recognized 文本 / Score 进度条 / Feedback 文字

---

## 数据流

```
启动 → load_dataset()
       ├── 真实 CSV → is_real=True
       └── mock data → is_real=False, 侧边栏警告
         ↓
选择 TOPIC → get_sentences_by_category()
         ↓
选择 SENTENCE → 主区域更新
         ↓
上传音频 → 点击 Analyze
         ↓
save_uploaded_file() → uploads/
         ↓
transcribe_audio(path) → 识别文本
         ↓
compare_texts(target, recognized) → 分数
         ↓
generate_feedback(score) → 反馈
         ↓
显示结果区域
```

---

## 样式方案

通过 `st.markdown("<style>...</style>", unsafe_allow_html=True)` 注入 CSS：

| 元素 | 效果 |
|------|------|
| 页面背景 | 米白色 `#f5f0eb` |
| Target sentence 卡片 | 暖灰色圆角卡片，替代默认蓝色 info box |
| Analyze 按钮 | 深色 `#2c2c2c`，白色文字 |
| Retry 按钮 | 白底，带边框 |

---

## 错误处理

| 情况 | 处理 |
|------|------|
| CSV 不存在 | 自动用 mock data，侧边栏黄色警告 |
| CSV 字段缺失 | 显示明确错误，告知缺少哪些字段 |
| 参考音频不存在 | 显示警告，页面正常运行 |
| 未上传文件点 Analyze | 显示警告，不执行识别 |
| ASR 报错 | try/except 捕获，显示错误信息 |
| uploads/ 不存在 | 自动创建 |

---

## 实现计划（三窗口分工）

### 窗口 2：实现 modules/

按以下顺序实现，每个文件完成后单独 git commit：

1. `modules/data_loader.py` — CSV 读取 + mock data fallback
2. `modules/asr_interface.py` — mock ASR 接口
3. `modules/comparison.py` — rapidfuzz 相似度计算
4. `modules/feedback.py` — 分数 → 反馈文字
5. `uploads/.gitkeep` — 保证目录被 git 追踪
6. `requirements.txt` — streamlit, pandas, rapidfuzz

### 窗口 3：实现 app.py + 收尾

1. `app.py` — 完整 Streamlit 主页面（CSS + 侧边栏 + 主区域 + 错误处理）
2. 验证：`streamlit run app.py` 全流程可用
3. `docs/architecture.md` — 架构说明文档
4. git commit + PR

---

## 验证标准

```
streamlit run app.py（无报错启动）
→ 选择 TOPIC（下拉菜单有内容）
→ 选择 SENTENCE（韩语句子显示正确）
→ 主区域显示目标句子和英文翻译
→ 上传音频文件
→ 点击 Analyze（出现结果区域）
→ 显示 Recognized / Score / Feedback
→ 点击 Retry（页面重置）
```
