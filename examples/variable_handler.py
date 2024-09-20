from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker
# from src.main import config
# logger = config.logger

def handle_task(task: ExternalTask) -> TaskResult:
    first_var = task.get_variable('firstVar')
    nr_var = task.get_variable('nrVar')

    # logger.info(f"Received string: {first_var}")
    # logger.info(f"Received integer: {nr_var}")
    print(f"Received string: {first_var}")
    print(f"Received integer: {nr_var}")

    result = TaskResult(
        success=True,
        task=task,
        global_variables={},
        local_variables={}
    )

    return result

if __name__ == "__main__":
    worker = ExternalTaskWorker(worker_id="my-worker", base_url="http://localhost:8088/engine-rest")
    worker.subscribe("variable_handler_topic", handle_task)