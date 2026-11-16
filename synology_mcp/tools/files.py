"""File Station tools: browse, inspect, search and manage files and folders."""

from __future__ import annotations

import asyncio

from .. import api
from ..app import check, fmt, mcp, ts

# Fields requested from File Station; must be sent as a JSON-array string.
_FILE_ADDITIONAL = '["real_path","size","time","type","owner","perm"]'


@mcp.tool()
async def list_shares() -> str:
    """List all available shared folders (File Station view)."""
    data = check(await api.call("SYNO.FileStation.List", "list_share", version=2,
                                additional='["real_path","perm"]'))
    shares = []
    for s in data.get("shares", []):
        shares.append({
            "name": s.get("name"),
            "path": s.get("path"),
            "real_path": s.get("additional", {}).get("real_path"),
            "is_readonly": s.get("additional", {}).get("perm", {}).get("is_readonly"),
        })
    return fmt({"shares": shares, "total": data.get("total", len(shares))})


@mcp.tool()
async def list_files(
    path: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "name",
    sort_direction: str = "asc",
    pattern: str | None = None,
) -> str:
    """
    List files and folders at a given path.

    Args:
        path: Full path e.g. /home or /docker/app
        limit: Max items to return (default 100)
        offset: Pagination offset
        sort_by: name | size | user | group | mtime | atime | crtime | posix
        sort_direction: asc | desc
        pattern: Optional filename filter (supports wildcards, e.g. *.pdf)
    """
    data = check(await api.call(
        "SYNO.FileStation.List", "list", version=2,
        folder_path=path, limit=limit, offset=offset,
        sort_by=sort_by, sort_direction=sort_direction,
        pattern=pattern, additional=_FILE_ADDITIONAL,
    ))
    files = []
    for f in data.get("files", []):
        add = f.get("additional", {})
        time = add.get("time", {})
        files.append({
            "name": f.get("name"),
            "path": f.get("path"),
            "is_dir": f.get("isdir"),
            "size_bytes": add.get("size") if not f.get("isdir") else None,
            "modified": ts(time.get("mtime")),
            "created": ts(time.get("crtime")),
        })
    return fmt({"path": path, "total": data.get("total", len(files)), "files": files})


@mcp.tool()
async def get_file_info(paths: str) -> str:
    """
    Get detailed info (size, owner, timestamps) for one or more files/folders.

    Args:
        paths: Comma-separated paths e.g. /home/report.pdf,/photo
    """
    data = check(await api.call(
        "SYNO.FileStation.List", "getinfo", version=2,
        path=paths, additional=_FILE_ADDITIONAL,
    ))
    files = []
    for f in data.get("files", []):
        add = f.get("additional", {})
        time = add.get("time", {})
        owner = add.get("owner", {})
        files.append({
            "name": f.get("name"),
            "path": f.get("path"),
            "is_dir": f.get("isdir"),
            "real_path": add.get("real_path"),
            "size_bytes": add.get("size") if not f.get("isdir") else None,
            "owner": f"{owner.get('user')}:{owner.get('group')}" if owner else None,
            "modified": ts(time.get("mtime")),
            "created": ts(time.get("crtime")),
            "accessed": ts(time.get("atime")),
        })
    return fmt({"files": files})


@mcp.tool()
async def get_directory_size(path: str) -> str:
    """
    Calculate the total size and item count of a folder (recursively).

    Args:
        path: Folder path e.g. /docker
    """
    start = check(await api.call("SYNO.FileStation.DirSize", "start", version=1, path=path))
    taskid = start.get("taskid")
    if not taskid:
        return fmt(start)
    for _ in range(120):
        status = check(await api.call("SYNO.FileStation.DirSize", "status", version=1, taskid=taskid))
        if status.get("finished"):
            total = int(status.get("total_size", 0) or 0)
            return fmt({
                "path": path,
                "total_size_bytes": total,
                "total_size_gb": round(total / 1024 ** 3, 2),
                "num_files": status.get("num_file"),
                "num_dirs": status.get("num_dir"),
            })
        await asyncio.sleep(0.5)
    return fmt({"error": "directory size calculation timed out"})


@mcp.tool()
async def get_file_md5(path: str) -> str:
    """
    Compute the MD5 checksum of a file.

    Args:
        path: Full file path
    """
    start = check(await api.call("SYNO.FileStation.MD5", "start", version=2, file_path=path))
    taskid = start.get("taskid")
    if not taskid:
        return fmt(start)
    for _ in range(120):
        status = check(await api.call("SYNO.FileStation.MD5", "status", version=2, taskid=taskid))
        if status.get("finished"):
            return fmt({"path": path, "md5": status.get("md5")})
        await asyncio.sleep(0.5)
    return fmt({"error": "MD5 calculation timed out"})


@mcp.tool()
async def search_files(
    folder_path: str,
    pattern: str,
    recursive: bool = True,
    limit: int = 50,
) -> str:
    """
    Search for files by name pattern within a folder.

    Args:
        folder_path: Root folder to search e.g. /home
        pattern: Filename pattern e.g. *.pdf or report*
        recursive: Search subdirectories (default True)
        limit: Max results (default 50)
    """
    start = check(await api.call(
        "SYNO.FileStation.Search", "start", version=2,
        folder_path=folder_path, recursive=recursive, pattern=pattern,
    ))
    taskid = start.get("taskid")
    if not taskid:
        return fmt(start)
    try:
        for _ in range(20):
            status = await api.call(
                "SYNO.FileStation.Search", "list", version=2,
                taskid=taskid, limit=limit,
                additional='["real_path","size","time"]',
            )
            if status.get("success"):
                data = status["data"]
                if data.get("finished") or data.get("files"):
                    files = [
                        {
                            "name": f.get("name"),
                            "path": f.get("path"),
                            "is_dir": f.get("isdir"),
                            "size_bytes": f.get("additional", {}).get("size") if not f.get("isdir") else None,
                            "modified": ts(f.get("additional", {}).get("time", {}).get("mtime")),
                        }
                        for f in data.get("files", [])
                    ]
                    return fmt({"found": len(files), "finished": data.get("finished"), "files": files})
            await asyncio.sleep(0.5)
        return fmt({"error": "search timed out"})
    finally:
        await api.call("SYNO.FileStation.Search", "stop", version=2, taskid=taskid)


