import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
import base64
import json
from camunda.external_task.external_task import ExternalTask, TaskResult
# from camunda.external_task.external_task_client import ExternalTaskClient
from camunda.external_task.external_task_worker import ExternalTaskWorker

def handle_task(task: ExternalTask, file_path) -> TaskResult:
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

if __name__ == "__main__":
    # client = ExternalTaskClient(
    #     base_url="http://localhost:8088/engine-rest",
    #     worker_id="my-worker",
    #     max_tasks=1,
    #     max_polling_interval=5000,
    #     async_response_timeout=5000,
    #     lock_duration=10000
    # )

    file_path = r"C:\Users\MarcosCa\Downloads\sample2.pdf"

    worker = ExternalTaskWorker(worker_id="my-worker", base_url="http://localhost:8088/engine-rest")
    # worker.subscribe("file_handler_topic", handle_task)
    worker.subscribe("file_handler_topic", lambda task: handle_task(task, file_path))
