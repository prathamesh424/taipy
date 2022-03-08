import os
import pickle
import shutil
from datetime import datetime

import pandas as pd
import pytest

from taipy.core.common.alias import CycleId, PipelineId, ScenarioId
from taipy.core.common.frequency import Frequency
from taipy.core.config.config import Config
from taipy.core.config.global_app_config import GlobalAppConfig
from taipy.core.config.job_config import JobConfig
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.cycle._cycle_model import _CycleModel
from taipy.core.cycle.cycle import Cycle
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.scope import Scope
from taipy.core.job._job_manager import _JobManager
from taipy.core.pipeline._pipeline_manager import _PipelineManager
from taipy.core.pipeline._pipeline_model import _PipelineModel
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.scenario._scenario_model import _ScenarioModel
from taipy.core.scenario.scenario import Scenario
from taipy.core.scheduler.scheduler_factory import SchedulerFactory
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task.task import Task

current_time = datetime.now()


@pytest.fixture(scope="function")
def csv_file(tmpdir_factory) -> str:
    csv = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.csv")
    csv.to_csv(str(fn), index=False)
    return fn.strpath


@pytest.fixture(scope="function")
def excel_file(tmpdir_factory) -> str:
    excel = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.xlsx")
    excel.to_excel(str(fn), index=False)
    return fn.strpath


@pytest.fixture(scope="function")
def excel_file_with_multi_sheet(tmpdir_factory) -> str:
    excel_multi_sheet = {
        "Sheet1": pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]),
        "Sheet2": pd.DataFrame([{"a": 7, "b": 8, "c": 9}, {"a": 10, "b": 11, "c": 12}]),
    }
    fn = tmpdir_factory.mktemp("data").join("df.xlsx")

    writer = pd.ExcelWriter(str(fn))
    for key in excel_multi_sheet.keys():
        excel_multi_sheet[key].to_excel(writer, key, index=False)
    writer.save()

    return fn.strpath


@pytest.fixture(scope="function")
def pickle_file_path(tmpdir_factory) -> str:
    data = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.p")
    pickle.dump(data, open(str(fn), "wb"))
    return fn.strpath


@pytest.fixture(scope="function")
def default_data_frame():
    return pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])


@pytest.fixture(scope="function")
def default_multi_sheet_data_frame():
    return {
        "Sheet1": pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]),
        "Sheet2": pd.DataFrame([{"a": 7, "b": 8, "c": 9}, {"a": 10, "b": 11, "c": 12}]),
    }


@pytest.fixture(autouse=True)
def cleanup_files():
    if os.path.exists(".data"):
        shutil.rmtree(".data")


@pytest.fixture(scope="function")
def current_datetime():
    return current_time


@pytest.fixture(scope="function")
def scenario(cycle):
    return Scenario("sc", [], {}, ScenarioId("sc_id"), current_time, is_master=False, tags={"foo"}, cycle=None)


@pytest.fixture(scope="function")
def data_node():
    return InMemoryDataNode("data_node_config_id", Scope.PIPELINE)


@pytest.fixture(scope="function")
def task(data_node):
    dn = InMemoryDataNode("dn_config_id", Scope.PIPELINE)
    return Task("task_config_id", print, [data_node], [dn])


@pytest.fixture(scope="function")
def scenario_model(cycle):
    return _ScenarioModel(
        ScenarioId("sc_id"),
        "sc",
        [],
        {},
        creation_date=current_time.isoformat(),
        master_scenario=False,
        subscribers=[],
        tags=["foo"],
        cycle=None,
    )


@pytest.fixture(scope="function")
def cycle():
    example_date = datetime.fromisoformat("2021-11-11T11:11:01.000001")
    return Cycle(
        Frequency.DAILY,
        {},
        creation_date=example_date,
        start_date=example_date,
        end_date=example_date,
        name="cc",
        id=CycleId("cc_id"),
    )


@pytest.fixture(scope="class")
def pipeline():
    return Pipeline("pipeline", {}, [], PipelineId("pipeline_id"))


@pytest.fixture(scope="function")
def cycle_model():
    return _CycleModel(
        CycleId("cc_id"),
        "cc",
        Frequency.DAILY,
        {},
        creation_date="2021-11-11T11:11:01.000001",
        start_date="2021-11-11T11:11:01.000001",
        end_date="2021-11-11T11:11:01.000001",
    )


@pytest.fixture(scope="class")
def pipeline_model():
    return _PipelineModel(PipelineId("pipeline_id"), None, "pipeline", {}, [], [])


@pytest.fixture(scope="function", autouse=True)
def setup():
    delete_everything()


def delete_everything():
    _TaskManager._scheduler = SchedulerFactory.build_scheduler
    _ScenarioManager._delete_all()
    _PipelineManager._delete_all()
    _DataManager._delete_all()
    _TaskManager._delete_all()
    _JobManager._delete_all()
    _CycleManager._delete_all()
    Config._python_config._global_config = GlobalAppConfig()
    Config._python_config._job_config = JobConfig()
    Config._python_config._data_nodes.clear()
    Config._python_config._tasks.clear()
    Config._python_config._pipelines.clear()
    Config._python_config._scenarios.clear()


@pytest.fixture(scope="function", autouse=True)
def teardown():
    delete_everything()
