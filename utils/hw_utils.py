import torch


def get_optimal_device_and_precision():
    """
    Detect optimal computational device (NVIDIA CUDA / Apple Silicon MPS / CPU)
    and whether FP16 half-precision execution should be activated.

    Returns:
        tuple: (device_str, use_half_bool)
    """
    if torch.cuda.is_available():
        # NVIDIA GPUs (Azure / PC) unlock high-speed Tensor Core performance with FP16
        return "cuda", True
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        # Apple Silicon (M1/M2/M3/M4) GPU acceleration via Metal Performance Shaders.
        # Retain FP32 on MPS to avoid PyTorch half-precision NMS kernel limitations on macOS.
        return "mps", False
    else:
        return "cpu", False


def get_inference_batch_size(device: str) -> int:
    """
    Calculate the optimal batch size depending on hardware architecture to prevent
    CPU RAM cache thrashing while maximizing GPU tensor pipeline saturation.
    """
    if device == "cuda":
        return 32  # Saturate NVIDIA CUDA VRAM pipelines
    elif device == "mps":
        return 16  # Optimal for unified Apple Silicon architecture
    else:
        return 8   # Prevent CPU memory swap thrashing on non-GPU instances
