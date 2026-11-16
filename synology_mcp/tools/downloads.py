"""Download Station tools (DSM 7 uses the DownloadStation2 API)."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp

_TASK_API = "SYNO.DownloadStation2.Task"


@mcp.tool()
async def list_downloads() -> str:
    """List Download Station tasks with progress, size and transfer speed."""
    data = check(await api.call(
        _TASK_API, "list", version=2,
        additional='["detail","transfer"]',
    ))
    tasks = []
    for t in data.get("task", []):
        add = t.get("additional", {})
        transfer = add.get("transfer", {})
        size = int(t.get("size", 0) or 0)
        done = int(transfer.get("size_downloaded", 0) or 0)
        tasks.append({
            "id": t.get("id"),
            "title": t.get("title"),
            "type": t.get("type"),
            "status": t.get("status"),
            "size_mb": round(size / 1024 ** 2, 1) if size else None,
            "progress_pct": round(done / size * 100, 1) if size else None,
            "download_kb_s": round(int(transfer.get("speed_download", 0) or 0) / 1024, 1),
            "upload_kb_s": round(int(transfer.get("speed_upload", 0) or 0) / 1024, 1),
        })
    return fmt({"total": data.get("total", len(tasks)), "tasks": tasks})


