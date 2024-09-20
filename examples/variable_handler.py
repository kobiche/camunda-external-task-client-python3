import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
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

    # result = TaskResult(
    #     success=True,
    #     task=task,
    #     global_variables={},
    #     local_variables={}
    # )

    # return result

    manipulated_string = first_var + first_var if first_var else None
    manipulated_integer = nr_var * 2 if nr_var else None

    print(f"Manipulated string: {manipulated_string}")
    print(f"Manipulated integer: {manipulated_integer}")

    variables = {
        "manipulatedString": manipulated_string,
        "manipulatedInteger": manipulated_integer
    }

    return task.complete(variables)
    

if __name__ == "__main__":
    worker = ExternalTaskWorker(worker_id="my-worker", base_url="http://localhost:8088/engine-rest")
    worker.subscribe("variable_handler_topic", handle_task)