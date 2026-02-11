import psutil
import GPUtil
import logging

# Configure module-level logger
logger = logging.getLogger(__name__)

def get_system_metrics():
    """
    Collects telemetry data from the host system.
    Returns:
        dict: containing 'cpu_usage', 'ram_usage', 'gpu_temp', etc.
    """
    metrics = {
        "cpu_usage": 0.0,
        "ram_usage": 0.0,
        "gpu_name": None,
        "gpu_temp": 0,
        "gpu_load": 0.0
    }

    try:
        # 1. CPU & RAM Metrics (psutil)
        # interval=1 is crucial for accurate CPU load calculation
        metrics["cpu_usage"] = psutil.cpu_percent(interval=1)
        metrics["ram_usage"] = psutil.virtual_memory().percent

        # 2. GPU Metrics (GPUtil)
        # Attempt to detect NVIDIA GPUs via driver
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            metrics["gpu_name"] = gpu.name
            metrics["gpu_temp"] = gpu.temperature
            metrics["gpu_load"] = gpu.load * 100  # Convert 0.5 to 50%
        else:
            # Non-critical: Driver not found or non-NVIDIA GPU
            pass

    except Exception as e:
        logger.error(f"Failed to fetch hardware metrics: {e}")

    return metrics