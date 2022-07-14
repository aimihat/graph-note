import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestSaveGraph:
    def test_returns_updated_graph(self):
        ...

    def test_adds_inputs(self):
        ...

    def test_saves_graph(self):
        ...

    def test_invalid_request_raises(self):
        ...


class TestRunCell:
    def test_runs_selected_cell(self):
        ...

    def test_does_not_run_other_cells(self):
        ...

    def test_updates_output_ports(self):
        ...
