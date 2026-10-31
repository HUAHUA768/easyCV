from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent
RESUME_FILE = BASE_DIR / "resume.yaml"
EXAMPLES_DIR = BASE_DIR / "examples"
APP_DIR = BASE_DIR  # where main resume.yaml lives

# Ensure examples directory exists
EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_resume_file() -> None:
    """Create the private working resume from the public example on first run."""
    if RESUME_FILE.exists():
        return
    example_file = EXAMPLES_DIR / "example.yaml"
    if not example_file.exists():
        raise FileNotFoundError(
            f"无法创建 {RESUME_FILE.name}: 示例文件 {example_file} 不存在"
        )
    RESUME_FILE.write_text(example_file.read_text(encoding="utf-8"), encoding="utf-8")


_ensure_resume_file()

app = FastAPI(title="easy-cv", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class ResumeRawPayload(BaseModel):
    yaml_text: str
    filename: str = "resume.yaml"


def _resolve_file(filename: str) -> Path:
    """Resolve a filename to its actual path."""
    if filename.startswith("examples/"):
        file_name = filename.split("/", 1)[1]
        return EXAMPLES_DIR / file_name
    return BASE_DIR / filename


def _find_yaml_files() -> List[Tuple[str, Path]]:
    """Find all .yaml/.yml files in both APP_DIR and EXAMPLES_DIR."""
    results = []
    seen = set()
    # Root level (resume.yaml)
    for f in sorted(BASE_DIR.glob("*.yaml")) + sorted(BASE_DIR.glob("*.yml")):
        name = f.name
        if name not in seen:
            results.append((name, f))
            seen.add(name)
    # Examples directory
    if EXAMPLES_DIR.exists():
        for f in sorted(EXAMPLES_DIR.glob("*.yaml")) + sorted(EXAMPLES_DIR.glob("*.yml")):
            name = f.name
            if name not in seen:
                results.append((f"examples/{name}", f))
                seen.add(name)
    return results


def _read_resume(filename: str = "resume.yaml") -> Dict[str, Any]:
    file_path = _resolve_file(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"{filename} 不存在")
    text = file_path.read_text(encoding="utf-8")
    parsed = yaml.safe_load(text) or {}
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=400, detail=f"{filename} 顶层必须是对象")
    return parsed


def _write_resume(data: Dict[str, Any], filename: str = "resume.yaml") -> None:
    file_path = _resolve_file(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


@app.get("/api/resume/files")
def list_yaml_files() -> List[Tuple[str, str]]:
    """Return list of available YAML files as [(display_name, filename)]."""
    files = _find_yaml_files()
    return [(name, name) for name, _ in files]


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/resume")


@app.get("/resume", response_class=HTMLResponse, include_in_schema=False)
def resume_page(
    request: Request,
    file: str = Query(default="resume.yaml"),
) -> HTMLResponse:
    data = _read_resume(file)
    return templates.TemplateResponse(
        request,
        "resume.html",
        context={
            "resume": data,
            "basics": data.get("basics", {}),
            "education": data.get("education", []),
            "code": data.get("code", []),
            "personal_docs": data.get("personal_docs"),
            "team_projects": data.get("team_projects", []),
            "personal_projects": data.get("personal_projects", []),
            "lab_tutorials": data.get("lab_tutorials", []),
            "skills": data.get("skills", []),
            "open_source_experience": data.get("open_source_experience", []),
            "project_experience": data.get("project_experience", []),
        },
    )


@app.get("/editor", response_class=HTMLResponse, include_in_schema=False)
def editor_page(
    request: Request,
    file: str = Query(default="resume.yaml"),
) -> HTMLResponse:
    file_path = _resolve_file(file)
    yaml_text = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
    return templates.TemplateResponse(
        request, "editor.html", context={"yaml_text": yaml_text}
    )


class ResumePayloadWithFilename(BaseModel):
    data: Dict[str, Any]
    filename: str = "resume.yaml"


@app.get("/api/resume")
def get_resume_data(file: str = Query(default="resume.yaml")) -> Dict[str, Any]:
    return _read_resume(file)


@app.put("/api/resume")
def put_resume_data(payload: ResumePayloadWithFilename) -> Dict[str, str]:
    _write_resume(payload.data, payload.filename)
    return {"message": f"已更新 {payload.filename}"}


@app.get("/api/resume/raw")
def get_resume_raw(file: str = Query(default="resume.yaml")) -> Dict[str, str]:
    file_path = _resolve_file(file)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"{file} 不存在")
    return {"yaml_text": file_path.read_text(encoding="utf-8"), "filename": file}


@app.put("/api/resume/raw")
def put_resume_raw(payload: ResumeRawPayload) -> Dict[str, str]:
    try:
        parsed = yaml.safe_load(payload.yaml_text) or {}
    except yaml.YAMLError as exc:
        raise HTTPException(status_code=400, detail=f"YAML 解析失败: {exc}") from exc
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=400, detail="YAML 顶层必须是对象")
    file_path = _resolve_file(payload.filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(payload.yaml_text, encoding="utf-8")
    return {"message": f"YAML 已保存为 {payload.filename}"}


if __name__ == "__main__":
    import sys
    import subprocess
    import platform

    host = "127.0.0.1"
    port = 8010

    if platform.system() == "Darwin":
        url = f"http://{host}:{port}"
        subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        import uvicorn
    except ImportError:
        print("uvicorn 未安装，请先运行: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    uvicorn.run("app:app", host=host, port=port, reload=True)
