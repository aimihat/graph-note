import pytest
import inspect
from execution.kernel import initialization
from execution.runner import GraphExecutor
import asyncio


class TestRunner:
    # @pytest.mark.asyncio
    # def test_init_kernel_runs_initialisation(self, mocker):
    #     initialization_src = inspect.getsource(initialization)
    #     mocked_client = mocker.Mock()
    #     mocked_client._async_execute_interactive = mocker.MagicMock()
    #     runner = GraphExecutor(mocked_client, None)
    #     asyncio.run(runner.initialize())
    #     mocked_client._async_execute_interactive.assert_called_with(
    #         initialization_src + " a"
    #     )

    def test_run_root(self):
        ...
        # test that root is validated

    def test_run_cell_validates(self):
        ...
        # test that cell is validated

        # test that cell is compiled

        # test that cell is executed

    def test_initialise_resets_outputs(self):
        ...

    def test_update_cell_output_overrides_stderr(self):
        """Both stdout and stderr should override cell output"""

    def test_update_cell_output_overrides_stdout(self):
        """Both stdout and stderr should override cell output"""
