# server.py
from fastmcp import FastMCP
from fastmcp.prompts import Message,UserMessage, AssistantMessage
from fastmcp import Context, FastMCP
import psutil
import os

# Create an MCP server
mcp = FastMCP("DifyMcp",host = "192.168.124.25",port = 9999)

# ----------------------- tools ---------------------------

@mcp.tool()
def get_system_overview() -> dict:
    """
    获取系统总体信息，包括CPU、内存、负载、进程数、PageCache大小。
    """
    cpu_times = psutil.cpu_times_percent()
    mem = psutil.virtual_memory()
    load1, load5, load15 = os.getloadavg()
    page_cache = psutil.swap_memory().sin  # 近似PageCache
    # 获取所有磁盘分区的使用情况
    disk_usages = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disk_usages.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            })
        except Exception:
            continue
    return {
        "cpu_percent": psutil.cpu_percent(),
        "cpu_user_percent": cpu_times.user,
        "cpu_system_percent": cpu_times.system,
        "cpu_cores": psutil.cpu_count(),
        "load1": load1,
        "load5": load5,
        "load15": load15,
        "total_memory": mem.total,
        "memory_percent": mem.percent,
        "process_count": len(psutil.pids()),
        "page_cache": page_cache,
        "disk_usages": disk_usages,
    }

@mcp.tool()
def get_top5_cpu_occupied_processes() -> dict:
    """
    获取CPU使用率最高的前五个进程及其使用率。
    """
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(p.info)
        except Exception:
            continue
    top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
    return {
        "top_5_cpu_occupied_processes": top_cpu,
    }

# ----------------------- prompts ---------------------------

@mcp.prompt()
def get_system_status(code_snippet: str) -> str:
    """评估当前系统的水位状况"""
    return f"请使用对应的工具来对当前系统的水位情况进行数据采集，并将采集得到的各种指标，基于你对于系统水位的理解（对总的资源情况和采集到的资源情况进行对比评估）来对系统水位进行评估"

if __name__ == "__main__":
    mcp.run(transport='sse')