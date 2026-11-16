"""Virtual Machine Manager tools."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp

_GUEST_API = "SYNO.Virtualization.API.Guest"


@mcp.tool()
async def list_virtual_machines() -> str:
    """List Virtual Machine Manager guests with their state and resource allocation."""
    data = check(await api.call(_GUEST_API, "list", version=1))
    guests = []
    for g in data.get("guests", []):
        guests.append({
            "name": g.get("guest_name"),
            "status": g.get("status"),
            "vcpus": g.get("vcpu_num"),
            "ram_mb": g.get("vram_size"),
            "storage": g.get("storage_name"),
            "autorun": g.get("autorun"),
            "description": g.get("description") or None,
        })
    guests.sort(key=lambda x: (x["status"] != "running", (x["name"] or "").lower()))
    return fmt({"total": len(guests), "guests": guests})


