# K-Read Coach：前端开发进度文档

> 本文档同时服务两个用途：**喂给 Agent 的技术规格参考** + **开发进度追踪记录**。
> 每个窗口完成后更新实施记录区块。

---

## ⚡ 开发进度一览

| 窗口 | 内容 | 状态 | 分支 / worktree |
|------|------|:----:|-----------------|
| 窗口 1 | 设计规划、技术决策 | ✅ 已完成 | — |
| 窗口 2 | `modules/` 全部模块 + `requirements.txt` | ✅ 已完成 | `claude/amazing-satoshi-053fa2` |
| 窗口 3 | `app.py` + 修复 + 文档 + PR | ⬜ 待实施 | `claude/amazing-satoshi-053fa2` |

**当前工作分支**：`feature-streamlit-ui`（worktree：`amazing-satoshi-053fa2`）

---

## 一、项目基础信息

### 1.1 项目背景

K-Read Coach 是一个面向非母语韩语学习者的朗读练习工具。

**核心定位**：Read-aloud practice tool（不是通用语音转文字，不是专业发音诊断）

**用户流程**：
```
选择预设韩语句子
  → 查看目标句子 + 英文翻译
  → 播放参考发音（data/clips/）
  → 自己模仿朗读并上传音频
  → Whisper small 识别用户音频
  → 比较识别文本与目标句子
  → 显示相似度分数 + 英文反馈
```

**仓库地址**：`https://github.com/tomkdf/K-Read-Coach`

### 1.2 分支说明

| 分支 | 负责人 | 用途 |
|------|--------|------|
| `main` | — | 最终合并，不一定含最新功能 |
| `develop-cleaning` | Tom | 数据清洗、CSV 生成、参考音频整理 |
| `feature-streamlit-ui` | 前端 | Streamlit 前端页面开发 ← **本文档的工作分支** |

> `develop-cleaning` 不是前端分支。它是 Tom 的数据清洗工作分支，已独立完成自己的任务。

### 1.3 团队分工

| 成员 | 负责内容 |
|------|----------|
| 前端（我） | Streamlit 页面、模块接口设计 |
| Tom | 数据清洗、CSV 生成、参考音频整理 |
| 法国同学 2 | Whisper small 模型、ASR 识别、Levenshtein / Jamo 评分 |

### 1.4 各成员工作状况

**Tom（数据清洗）**已完成：
- `dataset_cleaning.py`：从韩语语音数据集筛选日常短句并分类
- `extract_audio.py`：提取参考音频，压平为单层文件名，复制到 `data/clips/`，**同步更新 CSV `path` 字段为仅文件名**
- 产出：`data/k_read_coach_dataset.csv` + `data/clips/*.wav`

**ASR 成员**进展：
- 已验证 Whisper small 本地运行
- 使用 Levenshtein distance 评估，Jamo library 处理韩文
- 接口形式尚未确定（function / script / Docker / local API 之一）

**前端**：窗口 2 已完成全部模块，窗口 3 实施 `app.py`。

### 1.5 音频概念（严格区分）

| 音频类型 | 来源 | 位置 | 用途 |
|----------|------|------|------|
| Reference audio | 系统预设 | `data/clips/` | 给用户听目标发音 |
| User audio | 用户上传 | `uploads/` | 送给 Whisper 识别 |

**正确逻辑**：
- CSV `path` 指向 reference audio（`data/clips/xxx.wav`）
- 用户上传的是 user audio
- Whisper 只处理 user audio
- 系统比较 `sentence`（目标文本）和 `recognized_text`（识别结果）

---

## 二、架构设计（已确定）

### 2.1 文件结构

```
K-Read-Coach/
├── app.py                          ⬜ 窗口 3 实现
├── requirements.txt                ✅ 已完成
│
├── data/
│   ├── k_read_coach_dataset.csv    来自 develop-cleaning 分支
│   └── clips/
│       └── *.wav                   参考音频
│
├── uploads/
│   └── .gitkeep                    ✅ 已完成
│
├── modules/
│   ├── __init__.py                 ✅ 已完成（空文件）
│   ├── data_loader.py              ✅ 已完成
│   ├── asr_interface.py            ✅ 已完成（mock）
│   ├── comparison.py               ✅ 已完成（rapidfuzz）
│   └── feedback.py                 ✅ 已完成
│
└── docs/
    └── architecture.md             ⬜ 窗口 3 实现
```

### 2.2 模块化策略

前端与外部依赖（CSV、ASR）通过接口层隔离：

```
app.py
  ├── modules/data_loader.py    ← 隔离 CSV 格式变化
  ├── modules/asr_interface.py  ← 隔离 ASR 实现方式
  ├── modules/comparison.py     ← 隔离评分算法
  └── modules/feedback.py       ← 隔离反馈文本
```

**优点**：ASR 成员替换实现时，只需改 `transcribe_audio()` 内部，`app.py` 不动。

### 2.3 开发策略（Mock 优先）

```
优先搭建页面框架 → 优先定义接口 → 优先保证 App 可运行
     ↓
真实 CSV 未合并 → mock data（自动降级，侧边栏警告）
真实 ASR 未合并 → mock transcribe_audio()（固定返回 "안녕하세요"）
     ↓
等其他分支合并后，替换真实数据和真实 ASR，app.py 无需改动
```

---

## 三、实施记录

### 窗口 1：设计规划 ✅

**日期**：2026-05-09  
**产出**：`C:\Users\25142\.claude\plans\d-k-read-coach-k-read-coach-streamlit-a-refactored-storm.md`

**确认的设计决策**：

| 问题 | 决策 |
|------|------|
| 架构方式 | 模块化（4 模块 + app.py） |
| 相似度计算 | `rapidfuzz.fuzz.ratio()`（评估后优于 difflib） |
| 界面样式 | 少量自定义 CSS，暖色调（背景 `#f5f0eb`） |
| 音频输入 | 只支持文件上传（.wav / .mp3 / .m4a） |
| 结果展示 | 识别文本 + 相似度进度条 + 一句英文反馈 |
| Sentence 下拉内容 | 直接显示韩语句子 |

---

### 窗口 2：模块实现 ✅

**日期**：2026-05-09  
**分支**：`claude/amazing-satoshi-053fa2`  
**执行方式**：subagent-driven-development（每任务：实现 → 规格审查 → 质量审查 → commit）

#### Commit 记录

| Commit SHA | 内容 |
|------------|------|
| `8747386` | `feat: add data_loader module with CSV loading and mock data fallback` |
| `6ae229d` | `feat: add asr_interface module with mock transcribe_audio` |
| `8d476d1` | `feat: add comparison module using rapidfuzz for similarity scoring` |
| `ecdda85` | `feat: add feedback module with score-based English feedback generation` |
| `d50ff06` | `chore: add uploads directory with .gitkeep` |
| `a1aa810` | `chore: add requirements.txt with streamlit, pandas, rapidfuzz` |

#### 发现的问题与解决方案

**问题 1：Mock 数据 path 字段格式错误**

- **发现方式**：查看 Tom 的 GitHub 仓库（`develop-cleaning` 分支）`extract_audio.py`
- **根因**：`extract_audio.py` 用 `os.path.basename()` 压平路径后，CSV `path` 字段只含文件名（如 `1_0442.wav`），不含 `data/clips/` 前缀
- **窗口 2 的错误实现**：mock 数据写成 `"data/clips/greeting_01.wav"`
- **修复方案**：窗口 3 任务 1 修正为 `"greeting_01.wav"`，`app.py` 统一用 `Path("data/clips") / row["path"]` 拼接

**问题 2：文档预设 `difflib` vs 实际使用 `rapidfuzz`**

- **决策**：本文档第 9 节原建议 `difflib.SequenceMatcher`，实际实现采用 `rapidfuzz.fuzz.ratio()`（窗口 1 已确认此决策）
- **处理**：本文档第 4.3 节已更新为实际实现；接口返回结构不变，`app.py` 调用方式相同

**问题 3：代码质量审查发现的小问题（均已修复）**

- `data_loader.py`：缺失字段检测改用集合差异（`set` 运算）替代列表推导式
- `data_loader.py`：`get_categories()` 添加 `-> list[str]` 返回类型注解
- `data_loader.py`：移除第 35 行冗余的 `# type: pd.DataFrame` 行尾注释

---

### 窗口 3：app.py + 收尾 ⬜

**计划分支**：继续 `claude/amazing-satoshi-053fa2`  
**提示词文件**：`C:\Users\25142\.claude\plans\3-app-k-read-coach-window3.md`

**任务列表**：

| # | 任务 | commit |
|---|------|--------|
| 1 | 修复 `modules/data_loader.py` mock path（去掉 `data/clips/` 前缀） | `fix: normalize mock data path to filename-only format` |
| 2 | 实现 `app.py`（CSS + 侧边栏 + 主区域 + 完整分析流程） | `feat: implement Streamlit frontend with CSS styling and full analysis flow` |
| 3 | 创建 `docs/architecture.md` | `docs: add architecture overview` |
| 4 | 本地验证 + push + PR 到 `feature-streamlit-ui` | — |

---

## 四、技术规格（以实际实现为准）

### 4.1 CSV 数据接口 ✅ 已验证

**文件路径**：`data/k_read_coach_dataset.csv`

**字段**：

| 字段 | 含义 | 格式（已确认） |
|------|------|--------------|
| `path` | 参考音频文件名 | **仅文件名**，如 `1_0442.wav`（`extract_audio.py` 已压平） |
| `sentence` | 韩语目标句子 | 韩文字符串 |
| `english_translation` | 英文翻译 | 英文字符串 |
| `categories` | 分类标签 | 字符串，如 `"Greeting"` |

**前端音频路径拼接方式（已确认）**：
```python
CLIPS_DIR = "data/clips"
reference_audio_path = Path(CLIPS_DIR) / row["path"]
# 结果：data/clips/1_0442.wav
```

> ⚠️ 不要写 `"data/clips/" + row["path"]`，使用 `pathlib.Path` 拼接更安全。

**Mock data 格式（path 已修正）**：
```python
[
    {"path": "greeting_01.wav", "sentence": "안녕하세요", "english_translation": "Hello", "categories": "Greeting"},
    {"path": "school_01.wav",   "sentence": "학교에 갑니다", "english_translation": "I go to school", "categories": "School"},
]
```

### 4.2 `modules/data_loader.py` ✅ 已实现

**实际实现**（以代码为准，非原始草稿）：

```python
import os
import pandas as pd


def get_mock_dataset() -> pd.DataFrame:
    data = {
        'path': ['greeting_01.wav', 'school_01.wav'],   # 仅文件名
        'sentence': ['안녕하세요', '학교에 갑니다'],
        'english_translation': ['Hello', 'I go to school'],
        'categories': ['Greeting', 'School']
    }
    return pd.DataFrame(data)


def load_dataset(csv_path: str) -> tuple[pd.DataFrame, bool]:
    if not os.path.exists(csv_path):
        return (get_mock_dataset(), False)
    df = pd.read_csv(csv_path)
    required_fields = ['path', 'sentence', 'english_translation', 'categories']
    missing_fields = sorted(set(required_fields) - set(df.columns))
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    return (df, True)


def get_categories(df: pd.DataFrame) -> list[str]:
    return sorted(df['categories'].unique())


def get_sentences_by_category(df: pd.DataFrame, category: str) -> pd.DataFrame:
    return df[df['categories'] == category]
```

> **注**：`bool` 返回值含义：`True` = 真实 CSV；`False` = mock data。前端据此决定是否显示警告。

### 4.3 `modules/comparison.py` ✅ 已实现

> **与原始文档的差异**：使用 `rapidfuzz.fuzz.ratio()`，而非原草稿的 `difflib.SequenceMatcher`。接口和返回值格式不变。

```python
from rapidfuzz import fuzz


def compare_texts(target: str, recognized: str) -> dict:
    score = fuzz.ratio(target, recognized)
    return {
        "target": target,
        "recognized": recognized,
        "score": score      # float，0.0–100.0
    }
```

未来可替换为 Levenshtein / Jamo，前端只依赖 `score` 字段，`app.py` 无需改动。

### 4.4 `modules/asr_interface.py` ✅ 已实现（mock）

```python
def transcribe_audio(audio_path: str) -> str:
    # Mock implementation — returns fixed Korean text.
    # To integrate real ASR: replace only this function body.
    # Keep the signature (audio_path: str) -> str unchanged.
    # app.py does not need to be modified.
    return "안녕하세요"
```

**ASR 成员替换说明**：只改函数体内部，保持 `(audio_path: str) -> str` 签名不变。

### 4.5 `modules/feedback.py` ✅ 已实现

```python
def generate_feedback(score: float) -> str:
    if score >= 90:
        return "Excellent! Your pronunciation is very accurate."
    elif score >= 75:
        return "Good job! You're getting close to the target pronunciation."
    elif score >= 50:
        return "Keep practicing! Focus on the highlighted differences."
    else:
        return "Don't give up! Try listening to the reference audio again."
```

### 4.6 `app.py` ⬜ 窗口 3 实现

**CSS 样式注入**：
```python
st.markdown("""<style>
    .stApp { background-color: #f5f0eb; }
    /* Target sentence 卡片：暖灰色圆角 */
    /* Analyze 按钮：背景 #2c2c2c，白色文字 */
    /* Retry 按钮：白底，黑色边框 */
</style>""", unsafe_allow_html=True)
```

**页面结构**：

```
侧边栏                          主区域
─────────────────               ─────────────────────────────────
K-Read Coach                    Practice Session
Korean Read-Aloud Practice
                                Target Sentence 卡片（韩语）
[警告：Using mock dataset]       English Translation

TOPIC 下拉                       Reference Audio 播放器
SENTENCE 下拉                    （或警告：音频不存在 / mock 模式）

                                Your Reading 上传区（wav/mp3/m4a）

                                [Analyze ▶]    [Retry ↺]

                                ─────────────────────────────────
                                Result（Analyze 后出现）
                                Recognized Text
                                Similarity Score（进度条 + 百分比）
                                Feedback
```

**Analyze 调用链**：
```python
user_audio_path = save_uploaded_file(uploaded_file)
recognized_text = transcribe_audio(user_audio_path)          # asr_interface
result          = compare_texts(target_sentence, recognized_text)  # comparison
feedback        = generate_feedback(result["score"])          # feedback
```

**Retry**：`st.rerun()`

### 4.7 `requirements.txt` ✅ 已实现

```
streamlit
pandas
rapidfuzz
```

后续 ASR 成员接入时可能追加 `openai-whisper`、`python-Levenshtein`、`jamo`，由 ASR 成员负责添加。

---

## 五、对接待确认事项

### 5.1 与 Tom 确认（数据清洗）

| 问题 | 状态 | 结论 |
|------|:----:|------|
| CSV `path` 字段格式 | ✅ 已确认 | 仅文件名（`extract_audio.py` 压平），如 `1_0442.wav` |
| 参考音频位置 | ✅ 已确认 | 统一在 `data/clips/` |
| CSV 文件路径 | ❓ 待确认 | 预计 `data/k_read_coach_dataset.csv` |
| CSV 字段是否最终固定 | ❓ 待确认 | 预计 `path / sentence / english_translation / categories` |
| CSV 中是否有重复句子 | ❓ 待确认 | — |
| 是否需要唯一 ID 字段 | ❓ 待确认 | — |
| 分支合并时间 | ❓ 待确认 | `develop-cleaning` → `main` 或前端分支 |

### 5.2 与 ASR 成员确认

| 问题 | 状态 | 当前处理 |
|------|:----:|----------|
| 接口形式（function / script / Docker / API） | ❓ 待确认 | mock 函数占位 |
| 函数签名 | ❓ 建议 | `transcribe_audio(audio_path: str) -> str` |
| 是否需要 GPU | ❓ 待确认 | — |
| Levenshtein / Jamo 比较逻辑是否由 ASR 提供 | ❓ 待确认 | 前端当前用 rapidfuzz，后续可替换 |
| 比较函数返回格式 | ❓ 建议统一 | `{"target": str, "recognized": str, "score": float}` |

---

## 六、开发规范

### 6.1 Git 规则

```
只在 feature-streamlit-ui 分支开发前端
不要直接修改 develop-cleaning 分支
不要直接修改 main 分支
每个文件完成后单独 commit，通过 PR 合并
```

### 6.2 禁止事项

- 在 `app.py` 中直接加载 Whisper 模型
- 在前端重新选择 / 训练 / fine-tune 模型
- 把 `data/clips/` 里的参考音频当成用户输入
- 开发登录系统、数据库、复杂云部署
- 让前端强依赖其他分支已合并

### 6.3 验收清单（窗口 3 完成标准）

- [ ] `streamlit run app.py` 无报错启动
- [ ] mock 模式下侧边栏有 Greeting / School 两个话题
- [ ] 选句子后主区域正确显示韩语句子和英文翻译
- [ ] 上传任意音频 → Analyze → 出现 Recognized / Score / Feedback
- [ ] Score 进度条正常显示
- [ ] 参考音频不存在时显示 warning，页面不崩溃
- [ ] Retry 点击后页面重置
- [ ] 有真实 CSV 时能正确读取，字段缺失时给出清楚错误
