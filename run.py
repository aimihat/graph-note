import asyncio
from pathlib import Path

import jupyter_client

import test_dag
from graphnote.dag.runner import GraphRunner

KERNEL_SPEC_DIR = Path("/Users/aimilioshatzistamou/Library/Jupyter/runtime/")

client = jupyter_client.BlockingKernelClient()
client.load_connection_file(str(KERNEL_SPEC_DIR / "kernel-95354.json"))
client.start_channels()


async def main():
    runner = GraphRunner(client, test_dag.test_graph)
    await runner.init_kernel()
    await runner.run_dag_in_order()


asyncio.run(main())
