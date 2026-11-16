"""File-sharing protocols and terminal/SNMP services."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp

# protocol key -> (API, enable-field)
_SERVICES = {
    "smb": ("SYNO.Core.FileServ.SMB", "enable_samba"),
    "afp": ("SYNO.Core.FileServ.AFP", "enable_afp"),
    "nfs": ("SYNO.Core.FileServ.NFS", "enable_nfs"),
    "ftp": ("SYNO.Core.FileServ.FTP", "enable_ftp"),
}


@mcp.tool()
async def get_file_services() -> str:
    """Get the enabled state and key settings of SMB, AFP, NFS and FTP file services."""
    smb = check(await api.call("SYNO.Core.FileServ.SMB", "get", version=2))
    afp = check(await api.call("SYNO.Core.FileServ.AFP", "get", version=2))
    nfs = check(await api.call("SYNO.Core.FileServ.NFS", "get", version=2))
    ftp = check(await api.call("SYNO.Core.FileServ.FTP", "get", version=2))
    return fmt({
        "smb": {"enabled": smb.get("enable_samba"), "smb2": smb.get("enable_smb2"),
                "workgroup": smb.get("workgroup")},
        "afp": {"enabled": afp.get("enable_afp")},
        "nfs": {"enabled": nfs.get("enable_nfs"), "nfs_v4": nfs.get("enable_nfs_v4")},
        "ftp": {"enabled": ftp.get("enable_ftp"), "ftps": ftp.get("enable_ftps"),
                "port": ftp.get("portnum")},
    })


@mcp.tool()
async def get_terminal_settings() -> str:
    """Get SSH / Telnet terminal access settings."""
    data = check(await api.call("SYNO.Core.Terminal", "get", version=3))
    return fmt({
        "ssh_enabled": data.get("enable_ssh"),
        "ssh_port": data.get("ssh_port"),
        "telnet_enabled": data.get("enable_telnet"),
    })


@mcp.tool()
async def get_snmp_settings() -> str:
    """Get SNMP service settings."""
    data = check(await api.call("SYNO.Core.SNMP", "get", version=1))
    return fmt({
        "enabled": data.get("enable_snmp"),
        "v1v2_enabled": data.get("enable_snmp_v1v2"),
        "v3_enabled": data.get("enable_snmp_v3"),
        "location": data.get("location"),
        "contact": data.get("contact"),
    })
