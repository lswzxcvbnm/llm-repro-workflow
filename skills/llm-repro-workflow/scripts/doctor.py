#!/usr/bin/env python3
"""Read-only local hardware/environment report; Python 3.9+, no extra packages."""
import argparse
import ctypes
import datetime as dt
import importlib.metadata as md
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys


def redact(value):
    text = str(value)
    for key, secret in os.environ.items():
        if any(word in key.upper() for word in ("TOKEN", "PASSWORD", "SECRET", "API_KEY")):
            if len(secret) >= 6:
                text = text.replace(secret, "[REDACTED]")
    text = re.sub(r"(https?://)[^\s/@]+:[^\s/@]+@", r"\1[REDACTED]@", text)
    text = re.sub(r"(?i)([?&](?:token|key|api_key|signature|password)=)[^\s&]+", r"\1[REDACTED]", text)
    return re.sub(r"\bhf_[A-Za-z0-9]{12,}\b", "[REDACTED]", text)


def command(argv, timeout=15):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, errors="replace", timeout=timeout)
        return {"status": "ok" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": redact(result.stdout)[-12000:], "stderr": redact(result.stderr)[-6000:]}
    except FileNotFoundError:
        return {"status": "unavailable", "detail": "Executable not found"}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "detail": "Probe exceeded timeout"}
    except OSError as exc:
        return {"status": "failed", "detail": redact(exc)}


def memory_info():
    try:
        if sys.platform == "win32":
            class MemoryStatus(ctypes.Structure):
                _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
                    (key, ctypes.c_ulonglong) for key in
                    ("total", "available", "page_total", "page_available", "virtual_total", "virtual_available", "extended")]
            status = MemoryStatus()
            status.length = ctypes.sizeof(status)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                raise OSError("GlobalMemoryStatusEx failed")
            return {"status": "ok", "total_bytes": status.total, "available_bytes": status.available}
        if sys.platform.startswith("linux"):
            values = {}
            for line in Path("/proc/meminfo").read_text().splitlines():
                key, val = line.split(":", 1)
                values[key] = int(val.strip().split()[0]) * 1024
            return {"status": "ok", "total_bytes": values["MemTotal"], "available_bytes": values.get("MemAvailable")}
        if sys.platform == "darwin":
            result = command(["sysctl", "-n", "hw.memsize"])
            if result["status"] == "ok":
                return {"status": "partial", "total_bytes": int(result["stdout"].strip()),
                        "available_bytes": None, "detail": "Available RAM not inferred from free pages"}
    except (OSError, ValueError, KeyError) as exc:
        return {"status": "failed", "detail": redact(exc)}
    return {"status": "unavailable", "detail": "RAM probe unsupported on this platform"}


def cgroup_hints():
    results = {}
    if sys.platform.startswith("linux"):
        for name in ("memory.max", "memory.current", "cpu.max", "memory/memory.limit_in_bytes"):
            path = Path("/sys/fs/cgroup") / name
            try:
                if path.is_file():
                    results[name] = path.read_text().strip()
            except OSError:
                pass
    return {"values": results, "note": "Hints only; verify scheduler/container limits and nested cgroups separately"}


def disk_info(path):
    path = Path(path).expanduser().resolve()
    probe = path
    while not probe.exists() and probe.parent != probe:
        probe = probe.parent
    try:
        usage = shutil.disk_usage(probe)
        return {"status": "ok", "requested_path": str(path), "probed_path": str(probe),
                "total_bytes": usage.total, "free_bytes": usage.free}
    except OSError as exc:
        return {"status": "failed", "path": str(path), "detail": redact(exc)}


TORCH_PROBE = r'''
import json
import torch
r = {"version": torch.__version__, "cuda_build": torch.version.cuda,
     "hip_build": getattr(torch.version, "hip", None),
     "cuda_available": torch.cuda.is_available(), "devices": []}
r["cpu_operation"] = float((torch.ones(2, 2) @ torch.ones(2, 2)).sum()) == 8.0
if r["cuda_available"]:
    for index in range(torch.cuda.device_count()):
        with torch.cuda.device(index):
            p = torch.cuda.get_device_properties(index)
            free, total = torch.cuda.mem_get_info()
            value = (torch.ones(2, 2, device=f"cuda:{index}") @ torch.ones(2, 2, device=f"cuda:{index}")).sum().item()
            torch.cuda.synchronize()
            r["devices"].append({"index": index, "name": p.name,
                "compute_capability": list(torch.cuda.get_device_capability(index)),
                "free_bytes": free, "total_bytes": total,
                "bf16_supported": torch.cuda.is_bf16_supported() if hasattr(torch.cuda, "is_bf16_supported") else None,
                "operation_ok": value == 8.0})
mps = getattr(torch.backends, "mps", None)
r["mps_available"] = bool(mps and mps.is_available())
if r["mps_available"]:
    r["mps_operation"] = float((torch.ones(2, 2, device="mps") @ torch.ones(2, 2, device="mps")).sum().item()) == 8.0
print("LLM_REPRO_JSON=" + json.dumps(r))
if not r["cpu_operation"] or any(not d["operation_ok"] for d in r["devices"]) or r.get("mps_operation") is False:
    raise RuntimeError("Device arithmetic probe failed")
'''


def torch_info(timeout):
    result = command([sys.executable, "-I", "-c", TORCH_PROBE], timeout)
    for line in result.get("stdout", "").splitlines():
        if line.startswith("LLM_REPRO_JSON="):
            try:
                result["data"] = json.loads(line.split("=", 1)[1])
                result.pop("stdout", None)
            except ValueError:
                result["status"] = "failed"
    if result["status"] == "ok" and "data" not in result:
        result["status"] = "failed"
        result["detail"] = "Torch subprocess returned no structured report"
    return result


def dependency_check(mode, timeout):
    if mode == "none":
        return {"status": "not_requested"}
    if mode == "auto":
        mode = "pip" if importlib.util.find_spec("pip") else "uv"
    argv = [sys.executable, "-m", "pip", "check"] if mode == "pip" else ["uv", "pip", "check", "--python", sys.executable]
    result = command(argv, timeout)
    result["tool"] = mode
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--disk-path", action="append", default=[], help="Additional cache/data/output volume; repeatable")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--probe-torch", action="store_true", help="Import installed torch in a subprocess and run tiny CPU/visible accelerator operations")
    parser.add_argument("--check-deps", choices=("none", "auto", "pip", "uv"), default="none")
    parser.add_argument("--timeout", type=int, default=45, help="Seconds for each optional probe")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if an explicitly requested torch/dependency check cannot pass")
    args = parser.parse_args()
    if args.timeout < 1 or args.timeout > 60:
        parser.error("--timeout must be between 1 and 60 seconds")
    if not args.project.is_dir():
        parser.error("--project must be an existing directory")
    packages = {}
    for name in ("torch", "transformers", "datasets", "huggingface-hub", "accelerate", "peft", "numpy",
                 "deepspeed", "bitsandbytes", "flash-attn", "safetensors", "pip"):
        try:
            packages[name] = md.version(name)
        except md.PackageNotFoundError:
            packages[name] = None
    tools = {name: command([name, "--version"], timeout=10) for name in ("conda", "uv", "git", "nvcc")}
    report = {
        "schema_version": 1,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "Read-only local probes; no model download or experiment execution",
        "platform": {"system": platform.system(), "release": platform.release(), "machine": platform.machine(),
                     "processor": platform.processor(), "logical_cpus": os.cpu_count()},
        "python": {"executable": sys.executable, "version": platform.python_version(), "prefix": sys.prefix},
        "memory": memory_info(), "container_limits": cgroup_hints(),
        "disks": [disk_info(p) for p in [args.project] + args.disk_path],
        "tool_versions": tools, "packages": packages,
        "configuration": {key: redact(os.environ[key]) for key in
                          ("HF_HOME", "HF_ENDPOINT", "HF_HUB_OFFLINE", "HF_HUB_DISABLE_IMPLICIT_TOKEN", "UV_PROJECT_ENVIRONMENT") if key in os.environ},
        "proxy_configured": any(os.environ.get(key) for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")),
        "nvidia_smi": command(["nvidia-smi", "--query-gpu=index,name,driver_version,memory.total,memory.free,utilization.gpu", "--format=csv,nounits"], 15),
        "torch_probe": torch_info(args.timeout) if args.probe_torch else {"status": "not_requested"},
        "dependency_check": dependency_check(args.check_deps, args.timeout),
        "limitations": ["No network, repository scripts, dependency installs, or global configuration changes",
                        "Metadata checks do not establish ABI compatibility or model feasibility",
                        "Unavailable NVIDIA tools do not imply no AMD/Apple/Intel accelerators",
                        "Resource snapshots and cgroup hints must be checked against the actual job allocation"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(redact(json.dumps(report, ensure_ascii=False, indent=2)) + "\n", encoding="utf-8")
    failed = ((args.probe_torch and report["torch_probe"]["status"] != "ok") or
              (args.check_deps != "none" and report["dependency_check"]["status"] != "ok"))
    print(json.dumps({"report": str(args.output.resolve()), "torch": report["torch_probe"]["status"],
                      "dependencies": report["dependency_check"]["status"], "requested_checks_passed": not failed}, ensure_ascii=False))
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
