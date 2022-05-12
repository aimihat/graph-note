from ipykernel import ipkernel, kernelbase

# For the moment we use ipykernel, but if necessary in future - we can define a custom kernel.

if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=ipkernel.IPythonKernel)
