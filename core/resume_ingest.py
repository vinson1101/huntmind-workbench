"""
简历解析与候选人标准化模块

功能：
- 从统一文件对象中提取文本
- 标准化为面向决策层的 candidate 对象
- 记录失败项并输出统计信息
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import re

from docx import Document
from pypdf import PdfReader


SUPPORTED_TEXT_EXTENSIONS = {"txt", "md"}
SUPPORTED_WORD_EXTENSIONS = {"docx"}
SUPPORTED_PDF_EXTENSIONS = {"pdf"}
MAX_RAW_RESUME_LENGTH = 30000

NAME_LABEL_PATTERNS = [
    re.compile(r"(?:^|\n)\s*姓名\s*[:：]?\s*([^\n]{1,40})"),
    re.compile(r"(?:^|\n)\s*(?:Name|NAME|name)\s*[:：]?\s*([^\n]{1,40})"),
    re.compile(r"(?:^|\n)\s*(?:候选人|应聘者)\s*[:：]?\s*([^\n]{1,40})"),
]
NAME_STOPWORDS = {
    "个人简历",
    "简历",
    "求职简历",
    "应聘简历",
    "个人信息",
    "基本信息",
    "候选人",
    "应聘者",
    "姓名",
    "name",
    "resume",
    "cv",
}
NAME_REJECT_KEYWORDS = (
    "简历",
    "求职",
    "应聘",
    "岗位",
    "职位",
    "产品经理",
    "高级产品经理",
    "项目经理",
    "运营经理",
    "销售经理",
    "研发工程师",
    "工程师",
    "总监",
    "经理",
    "工作经历",
    "教育经历",
    "项目经历",
    "自我评价",
    "个人优势",
    "求职意向",
    "基本信息",
    "联系方式",
    "电话",
    "手机",
    "邮箱",
    "微信",
    "现居",
    "地址",
    "本科",
    "硕士",
    "博士",
)


def ingest_resume_files(
    resume_files: List[Any],
    extract_contact: bool = False,
) -> Dict[str, Any]:
    """
    批量解析简历文件并输出符合决策层输入契约的 candidates[]。

    Args:
        resume_files: 统一文件对象列表。对象应尽量提供：
            - source_platform
            - file_id
            - file_name
            - file_path
            - file_bytes
            - file_url
            - folder_id
            - channel
            - mime_type
        extract_contact: 预留参数，当前版本不做复杂字段抽取。

    Returns:
        {
            "candidates": [...],
            "stats": {...},
            "failures": [...]
        }
    """
    del extract_contact  # 当前版本只做稳定入模，不做复杂抽取

    candidates: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []

    for file_obj in resume_files:
        file_meta = _extract_file_meta(file_obj)

        try:
            raw_resume, parse_method = _extract_resume_text(file_obj, file_meta)
            raw_resume, is_truncated = _normalize_resume_text(raw_resume)

            if not raw_resume:
                raise ValueError("resume text empty")

            candidate = _build_candidate(file_meta, raw_resume, parse_method, is_truncated)
            candidates.append(candidate)
        except Exception as exc:
            failures.append(
                {
                    "file_id": file_meta["file_id"],
                    "file_name": file_meta["file_name"],
                    "status": "failed",
                    "reason": str(exc),
                }
            )

    return {
        "candidates": candidates,
        "stats": {
            "total_files": len(resume_files),
            "success_count": len(candidates),
            "failed_count": len(failures),
        },
        "failures": failures,
    }


def _extract_file_meta(file_obj: Any) -> Dict[str, str]:
    file_name = _get_attr(file_obj, "file_name") or _get_attr(file_obj, "name") or "unknown_resume"
    file_path = _get_attr(file_obj, "file_path") or ""
    file_id = _get_attr(file_obj, "file_id") or _stable_file_id(file_name, file_path)

    return {
        "source_platform": _get_attr(file_obj, "source_platform") or "local",
        "file_id": str(file_id),
        "file_name": str(file_name),
        "file_path": str(file_path),
        "file_url": str(_get_attr(file_obj, "file_url") or ""),
        "folder_id": str(_get_attr(file_obj, "folder_id") or ""),
        "channel": str(_get_attr(file_obj, "channel") or ""),
        "mime_type": str(_get_attr(file_obj, "mime_type") or ""),
    }


def _build_candidate(
    file_meta: Dict[str, str],
    raw_resume: str,
    parse_method: str,
    is_truncated: bool,
) -> Dict[str, Any]:
    candidate_id = f"{file_meta['source_platform']}_{file_meta['file_id']}"
    name, name_source = _extract_name(file_meta["file_name"], raw_resume)

    source = {
        "platform": file_meta["source_platform"],
        "channel": file_meta["channel"],
        "file_id": file_meta["file_id"],
        "file_name": file_meta["file_name"],
        "folder_id": file_meta["folder_id"],
        "file_url": file_meta["file_url"],
    }
    source = {key: value for key, value in source.items() if value}

    candidate: Dict[str, Any] = {
        "id": candidate_id,
        "name": name,
        "raw_resume": raw_resume,
        "extra_info": f"source={file_meta['source_platform']}; file_name={file_meta['file_name']}",
        "ingestion_meta": {
            "parse_status": "success",
            "parse_method": parse_method,
            "text_length": len(raw_resume),
            "is_truncated": is_truncated,
            "name_source": name_source,
        },
    }

    if source:
        candidate["source"] = source

    return candidate


def _extract_resume_text(file_obj: Any, file_meta: Dict[str, str]) -> Tuple[str, str]:
    file_name = file_meta["file_name"]
    file_path = file_meta["file_path"]
    extension = Path(file_name).suffix.lower().lstrip(".")

    file_bytes = _get_attr(file_obj, "file_bytes")
    if isinstance(file_bytes, str):
        file_bytes = file_bytes.encode("utf-8")

    if extension in SUPPORTED_TEXT_EXTENSIONS:
        if file_bytes is not None:
            return _decode_text_bytes(file_bytes), "text_bytes"
        if file_path:
            return Path(file_path).read_text(encoding="utf-8", errors="ignore"), "text_file"

    if extension in SUPPORTED_WORD_EXTENSIONS:
        if not file_path:
            raise ValueError("docx file_path missing")
        return _read_docx_text(Path(file_path)), "docx"

    if extension in SUPPORTED_PDF_EXTENSIONS:
        if file_path:
            return _read_pdf_text(Path(file_path)), "pdf"
        raise ValueError("pdf file_path missing")

    if file_bytes is not None:
        return _decode_text_bytes(file_bytes), "bytes_fallback"

    if file_path:
        return Path(file_path).read_text(encoding="utf-8", errors="ignore"), "file_fallback"

    raise ValueError(f"unsupported resume file: {file_name}")


def _normalize_resume_text(raw_text: str) -> Tuple[str, bool]:
    text = raw_text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    is_truncated = len(text) > MAX_RAW_RESUME_LENGTH
    if is_truncated:
        text = text[:MAX_RAW_RESUME_LENGTH].rstrip()

    return text, is_truncated


def _extract_name(file_name: str, raw_resume: str) -> Tuple[str, str]:
    content_name = _extract_name_from_resume(raw_resume)
    if content_name:
        return content_name, "resume_content"

    file_name_name = _extract_name_from_file_name(file_name)
    if file_name_name:
        return file_name_name, "file_name_fallback"

    first_line = next((line.strip() for line in raw_resume.splitlines() if line.strip()), "")
    first_line = _sanitize_name_candidate(first_line[:50])
    if _looks_like_resume_name(first_line):
        return first_line, "first_line_fallback"

    return "未知候选人", "unknown"


def _extract_name_from_resume(raw_resume: str) -> Optional[str]:
    lines = [_normalize_line(line) for line in raw_resume.splitlines()]
    lines = [line for line in lines if line][:30]
    if not lines:
        return None

    text_window = "\n".join(lines)

    for pattern in NAME_LABEL_PATTERNS:
        for match in pattern.finditer(text_window):
            for candidate in _candidate_name_tokens_from_line(match.group(1)):
                if _looks_like_resume_name(candidate):
                    return candidate

    for line in lines[:8]:
        for candidate in _candidate_name_tokens_from_line(line):
            if _looks_like_resume_name(candidate):
                return candidate

    return None


def _extract_name_from_file_name(file_name: str) -> Optional[str]:
    stem = Path(file_name).stem.strip()
    if not stem:
        return None

    for token in reversed(re.split(r"[_\-\s]+", stem)):
        candidate = _sanitize_name_candidate(token)
        if _looks_like_resume_name(candidate):
            return candidate

    for candidate in _candidate_name_tokens_from_line(stem):
        if _looks_like_resume_name(candidate):
            return candidate

    return None


def _candidate_name_tokens_from_line(line: str) -> List[str]:
    normalized = _sanitize_name_candidate(line)
    if not normalized:
        return []

    candidates: List[str] = [normalized]

    label_stripped = re.sub(r"^(姓名|Name|NAME|name|候选人|应聘者)\s*[:：]?\s*", "", normalized).strip()
    if label_stripped and label_stripped not in candidates:
        candidates.append(label_stripped)

    first_segment = re.split(r"[|｜/\\,，;；·•]", label_stripped, maxsplit=1)[0].strip()
    if first_segment and first_segment not in candidates:
        candidates.append(first_segment)

    first_token = re.split(r"\s+", label_stripped, maxsplit=1)[0].strip()
    if first_token and first_token not in candidates:
        candidates.append(first_token)

    chinese_match = re.match(r"^([\u4e00-\u9fff·]{2,8})(?:\s|$|[|｜/\\,，;；])", label_stripped)
    if chinese_match:
        candidates.append(chinese_match.group(1))

    return [_sanitize_name_candidate(candidate) for candidate in candidates if _sanitize_name_candidate(candidate)]


def _normalize_line(line: str) -> str:
    cleaned = line.strip()
    cleaned = cleaned.replace("\u3000", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _sanitize_name_candidate(value: str) -> str:
    text = value.strip()
    text = text.strip(" |｜/\\,，;；:：-_")
    text = re.sub(r"^(姓名|Name|NAME|name|候选人|应聘者)\s*[:：]?\s*", "", text).strip()
    text = re.sub(r"\s+", " ", text)

    text = re.split(
        r"(?:\b(?:男|女|女士|先生)\b|手机|电话|邮箱|微信|现居|住址|地址|出生年月|年龄|工作年限|教育经历|工作经历|求职意向)",
        text,
        maxsplit=1,
    )[0].strip()

    text = text.strip(" |｜/\\,，;；:：-_")
    return text


def _looks_like_resume_name(value: str) -> bool:
    text = _sanitize_name_candidate(value)
    if not text:
        return False

    if text.lower() in NAME_STOPWORDS:
        return False

    if any(keyword.lower() in text.lower() for keyword in NAME_REJECT_KEYWORDS):
        return False

    if re.search(r"\d", text):
        return False

    if "@" in text or re.search(r"(?:\+?86)?1[3-9]\d{9}", text):
        return False

    if len(text) > 30:
        return False

    if re.fullmatch(r"[\u4e00-\u9fff·]{2,8}", text):
        return True

    if re.fullmatch(r"[A-Za-z][A-Za-z .'-]{1,29}", text):
        return True

    return False


def _read_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


def _read_docx_text(path: Path) -> str:
    document = Document(str(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _decode_text_bytes(file_bytes: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("unable to decode text bytes")


def _get_attr(file_obj: Any, key: str) -> Optional[Any]:
    if isinstance(file_obj, dict):
        return file_obj.get(key)
    return getattr(file_obj, key, None)


def _stable_file_id(file_name: str, file_path: str) -> str:
    base = file_path or file_name or "unknown_resume"
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_")
    return normalized[:80] or "unknown_resume"
