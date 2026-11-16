"""Backup monitoring: Hyper Backup tasks."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def list_backup_tasks() -> str:
    """List Hyper Backup tasks with their current state and target."""
    data = check(await api.call("SYNO.Backup.Task", "list", version=1))
    tasks = []
    for t in data.get("task_list", []):
        tasks.append({
            "task_id": t.get("task_id"),
            "name": t.get("name"),
            "state": t.get("state"),
            "status": t.get("status"),
            "target": t.get("target_id"),
            "type": t.get("type"),
            "encrypted": t.get("data_enc"),
        })
    return fmt({
        "total": data.get("total", len(tasks)),
        "restoring": data.get("is_restoring"),
        "tasks": tasks,
    })




@mcp.tool()
async def get_backup_log(task_id: int | None = None, limit: int = 50) -> str:
    """
    Read Hyper Backup log entries (newest first), including the error reason.

    Args:
        task_id: Only this task (from list_backup_tasks); omit for all tasks
        limit: Maximum number of entries
    """
    data = check(await api.call(
        "SYNO.SDS.Backup.Client.Common.Log", "list", version=1,
        task_id=task_id, offset=0, limit=limit,
    ))
    return fmt(data)
