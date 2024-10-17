import json
import asyncio
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.async_external_task_worker import AsyncExternalTaskWorker
from camunda.external_task.file_utils import save_file_from_base64, create_encoded_file_variables #set_task_variables
# from src.main import config
# logger = config.logger

# def handle_file_task(task: ExternalTask, file_path) -> TaskResult:
#     input_file = task.get_variable("inputFile")
#     save_path = task.get_variable("savePath")

#     if input_file:
#         file_data_base64 = input_file.get("data")
#         save_file_from_base64(file_data_base64, save_path)
#         result_variables = set_task_variables(file_path)
#     else:
#         print("No file found in task.")
#         result_variables = {}

#     return task.complete(result_variables)

def handle_file_task(task: ExternalTask) -> TaskResult:
    input_file = task.get_variable("inputFile")
    save_path = task.get_variable("savePath")
    file_name = task.get_variable("fileName") or "default_name.pdf"
    content_type = task.get_variable("contentType") or "application/pdf"

    if input_file and save_path:
        file_data_base64 = input_file.get("data")
        save_file_from_base64(file_data_base64, save_path)
        result_variables = create_encoded_file_variables(save_path, file_name, save_path, content_type)
    else:
        print("Required variables are missing in task.")
        result_variables = {}

    return task.complete(result_variables)

def handle_variable_task(task: ExternalTask) -> TaskResult:
    first_var = task.get_variable('firstVar')
    nr_var = task.get_variable('nrVar')

    print(f"Received string: {first_var}")
    print(f"Received integer: {nr_var}")

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
    file_path = r"C:\Users\MarcosCa\Downloads\sample2.pdf"

    worker = AsyncExternalTaskWorker(worker_id="my-worker", base_url="http://localhost:8088/engine-rest")
    asyncio.run(worker.subscribe({
        "variable_handler_topic": lambda task: handle_variable_task(task),
        "file_handler_topic": lambda task: handle_file_task(task, file_path)
    }))
