from pathlib import Path
import subprocess

ROOT_DIR = Path(__file__).parent.parent.parent

KERNEL_SPEC_DIR = ROOT_DIR / ".kernelspecs"
CONNECT_FILE_PATH = KERNEL_SPEC_DIR / "kernel.json"


def start_kernel():
    subprocess.Popen(["python", str(ROOT_DIR / "kernel" / "launcher.py")])


# For the moment we use ipykernel, but if necessary in future - we can define a custom kernel.
if __name__ == "__main__":
    import sys

    sys.path.append(str(ROOT_DIR))
    from ipykernel import ipkernel
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(
        kernel_class=ipkernel.IPythonKernel, connection_file=str(CONNECT_FILE_PATH)
    )
