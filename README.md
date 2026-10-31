# easyCV

一个 Yaml 文件定义所有内容，实时预览，在线编辑，可一键导出 PDF，不用装任何软件，可丝滑接入各种skill

[示例简历 PDF](https://github.com/lvy010/X-Plore/blob/main/data/CV.pdf)

克隆仓库 → 启动服务 → 自动创建 `resume.yaml` → 编辑简历并预览、导出。

> `resume.yaml` 包含个人简历信息，已加入 `.gitignore`，不会提交到 GitHub。
> 第一次启动时，程序会自动将 `examples/example.yaml` 复制为根目录的 `resume.yaml`；
> 后续只需编辑这个本地文件即可。

## Preview

```
http://localhost:8010/resume    ← 简历预览（带「导出 PDF」按钮）
http://localhost:8010/editor    ← 左侧 YAML 编辑 + 右侧实时预览
```

![编辑器](./png/edit.png)

![导出 PDF](./png/pdf.png)

## Quick Start

**macOS**（需要 Python 3.9+，没有先 `brew install python`）

```bash
git clone https://github.com/lvy010/easyCV.git
cd easyCV
bash start.sh          # 自动建环境、装依赖、启动，并打开浏览器
```

**Linux**

```bash
git clone https://github.com/lvy010/easyCV.git
cd easyCV
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8010
```

**Windows**

```bash
git clone https://github.com/lvy010/easyCV.git
cd easyCV


conda create -n easycv python=3.9 -y


conda activate easycv


pip install -r requirements.txt


uvicorn app:app --reload --host 0.0.0.0 --port 8010
```

启动后访问 [http://localhost:8010](http://localhost:8010)。

## 以后每次启动只需两步
```bash
conda activate easycv

uvicorn app:app --reload --host 0.0.0.0 --port 8010

```
## How It Works

```
resume.yaml          ← 你的简历数据（唯一需要编辑的文件）
templates/resume.html ← Jinja2 渲染模板
static/style.css      ← 样式（蓝色主题，A4 排版，打印友好）
app.py                ← FastAPI 服务
```

### 编辑简历

**方式 A**：直接编辑 `resume.yaml`，保存后刷新页面。

**方式 B**：打开 `/editor`，在浏览器内编辑 YAML，点击保存，右侧实时预览。

### 导出 PDF

预览页顶部有「导出 PDF」按钮，点击后调用浏览器打印，选择"另存为 PDF"即可。

> 建议使用 Chrome/Edge，打印时取消页眉页脚，边距选"无"，效果最佳。

预览页顶部的「导出图片」按钮可以将整份简历下载为 PNG 图片。该功能需要浏览器能够加载 html2canvas CDN 资源。

## YAML Structure

```yaml
basics:           # 姓名、岗位、联系方式
education:        # 学习经历
code:             # 代码链接（GitHub、作品集等）
personal_docs:    # 个人文档/博客/专栏
team_projects:    # 团队项目（公司、Hackathon 等；当前默认 resume.yaml 暂时隐藏）
personal_projects: # 个人项目
lab_tutorials:    # 实验教程
```

完整示例见 [`examples/example.yaml`](./examples/example.yaml)。示例文件包含所有模块，其中包括 `team_projects`。如果本地 `resume.yaml` 暂时隐藏“团队项目”，模板仍保留该模块；需要展示时，在 `resume.yaml` 中添加 `team_projects` 数据即可。

项目描述较长或包含双引号时，建议使用 YAML 折叠多行文本，避免转义问题：

```yaml
text: >-
  这里可以继续写很长的项目描述，内部的“双引号”无需额外转义。
```

列表中的长内容也使用相同写法：

```yaml
items:
  - >-
    这里可以继续写很长的工作内容，内部的“双引号”无需额外转义。
```

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/resume` | HTML 简历预览 |
| `GET`  | `/editor` | YAML 编辑器 |
| `GET`  | `/api/resume` | JSON 格式简历数据 |
| `PUT`  | `/api/resume` | JSON 覆盖更新 |
| `GET`  | `/api/resume/raw` | 获取原始 YAML |
| `PUT`  | `/api/resume/raw` | 保存原始 YAML |
| `GET`  | `/docs` | OpenAPI 文档 |

## Docker

```bash
docker build -t easy-cv .
docker run -p 8010:8010 easy-cv
```

Acknowledgements
- https://github.com/hijiangtao/resume
- https://github.com/yamlresume/yamlresume

## License

MIT
