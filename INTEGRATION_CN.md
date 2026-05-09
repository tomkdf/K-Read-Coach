# K-Read Coach 对接说明

本文档说明数据清洗模块和 Whisper ASR 模块如何与前端对接。

---

## 对接说明一：数据清洗队友（Tom）

**你的输出如何与前端对接**

你在 `develop-cleaning` 分支上产出的文件，前端直接读取，**不需要你改任何代码**，只需在合并时确保以下两项。

### 文件放置位置

```
K-Read-Coach/
├── data/
│   ├── k_read_coach_dataset.csv   ← 清洗输出，放这里
│   └── clips/
│       ├── 1_0442.wav             ← 所有音频文件，扁平放这里
│       ├── 3_3106.wav
│       └── ...
```

### CSV 格式要求（你的输出已满足）

| 列名 | 类型 | 说明 |
|------|------|------|
| `path` | str | **仅文件名**，如 `3_3106.wav`，不含目录前缀 |
| `sentence` | str | 韩语原文 |
| `english_translation` | str | 英文翻译 |
| `categories` | str | 主题分类标签 |

编码：`UTF-8-SIG`（你现在的输出）可正常读取，无需修改。

### 验证方法

合并后在项目根目录运行以下命令，`is_real` 输出 `True` 即表示对接成功：

```bash
python -c "
from modules.data_loader import load_dataset
df, is_real = load_dataset('data/k_read_coach_dataset.csv')
print('is_real:', is_real)
print('行数:', len(df))
print('分类:', df['categories'].unique().tolist())
"
```

---

## 对接说明二：Whisper 队友

**你只需要修改一个文件**

### 文件位置

```
modules/asr_interface.py
```

### 当前内容（mock 实现）

```python
def transcribe_audio(audio_path: str) -> str:
    return "안녕하세요"   # ← 把这里替换成 Whisper 调用
```

### 你需要做的

只改这一个函数的函数体，**函数签名不能变**：

```python
import whisper   # 或 faster-whisper，取决于你选择的库

def transcribe_audio(audio_path: str) -> str:
    model = whisper.load_model("base")      # 或 "small" / "medium"
    result = model.transcribe(audio_path, language="ko")
    return result["text"]
```

### 约束

| 项目 | 要求 |
|------|------|
| 函数名 | `transcribe_audio`，不能改 |
| 参数 | `audio_path: str`，音频文件的本地路径 |
| 返回值 | `str`，转录出的韩语文字 |
| 修改范围 | **只改 `modules/asr_interface.py`，不动其他文件** |

### 依赖添加

在 `requirements.txt` 末尾加上你使用的库，例如：

```
openai-whisper
```

或：

```
faster-whisper
```

### 测试方法

```python
from modules.asr_interface import transcribe_audio
result = transcribe_audio("path/to/test_audio.wav")
print(result)   # 应输出韩语文字
```
