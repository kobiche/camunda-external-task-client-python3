import base64
import json
import asyncio
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.async_external_task_worker import AsyncExternalTaskWorker
from camunda.client.external_task_client import ENGINE_LOCAL_BASE_URL
# from src.main import config
# logger = config.logger

def handle_file_task(task: ExternalTask, file_path) -> TaskResult:
    input_file = task.get_variable("inputFile")
    save_path = task.get_variable("savePath")

    if input_file:
        file_data = base64.b64decode(input_file.get("data"))
        save_file(file_data, save_path)
        result_variables = set_task_variables(task, file_path)
    else:
        print("No file found in task.")

    return task.complete(result_variables)

def save_file(file_data, save_path):
    with open(save_path, "wb") as file:
        file.write(file_data)
    print(f"File saved to {save_path}")

def read_and_encode_file(file_path):
    with open(file_path, "rb") as file:
        file_data = file.read()
    return base64.b64encode(file_data).decode("utf-8")

def set_task_variables(task: ExternalTask, file_path):
    encoded_file_content = read_and_encode_file(file_path)

    encoded_file = {
        "data": encoded_file_content,
        "name": "testname.pdf",
        "encoding": "utf-8",
        "contentType": "application/pdf",
        "objectTypeName": "de.cib.cibflow.api.files.FileValueDataSource"
    }

    encoded_file_json = json.dumps(encoded_file)

    return {
        "replaced_file": {
            "value": json.dumps(encoded_file),
            "type": "Object",
            "valueInfo": {
                'type': 'Object',
                'objectTypeName': 'de.cib.cibflow.api.files.FileValueDataSource',
                'serializationDataFormat': 'application/json'
            }
        },
        "savePath": {"value": "sample2.pdf", "type": "String"}
    }

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