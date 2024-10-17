import base64
import json

def save_file_from_base64(file_data_base64, save_path):
    """Saves a file from a base64-encoded string."""
    file_data = base64.b64decode(file_data_base64)
    with open(save_path, "wb") as file:
        file.write(file_data)
    print(f"File saved to {save_path}")

def read_file_and_encode_to_base64(file_path):
    """Reads a file and returns its content encoded in base64."""
    with open(file_path, "rb") as file:
        file_data = file.read()
    return base64.b64encode(file_data).decode("utf-8")

def create_encoded_file_variables(file_path, file_name, save_path, content_type="application/pdf"):
    """Creates the task variables with the encoded file."""
    encoded_file_content = read_file_and_encode_to_base64(file_path)
    encoded_file = {
        "data": encoded_file_content,
        "name": file_name,
        "encoding": "utf-8",
        "contentType": content_type,
        "objectTypeName": "de.cib.cibflow.api.files.FileValueDataSource"
    }
    variables = {
        "replaced_file": {
            "value": json.dumps(encoded_file),
            "type": "Object",
            "valueInfo": {
                'type': 'Object',
                'objectTypeName': 'de.cib.cibflow.api.files.FileValueDataSource',
                'serializationDataFormat': 'application/json'
            }
        },
        "savePath": {"value": save_path, "type": "String"}
    }
    return variables

# def create_encoded_file_variable(file_path, file_name, content_type="application/pdf"):
#     """Creates an encoded file variable for the task."""
#     encoded_file_content = read_file_and_encode_to_base64(file_path)
#     encoded_file = {
#         "data": encoded_file_content,
#         "name": file_name,
#         "encoding": "utf-8",
#         "contentType": content_type,
#         "objectTypeName": "de.cib.cibflow.api.files.FileValueDataSource"
#     }
#     return encoded_file

# def set_task_variables(file_path):
#     encoded_file = create_encoded_file_variable(file_path, "testname.pdf")
#     return {
#         "replaced_file": {
#             "value": json.dumps(encoded_file),
#             "type": "Object",
#             "valueInfo": {
#                 'type': 'Object',
#                 'objectTypeName': 'de.cib.cibflow.api.files.FileValueDataSource',
#                 'serializationDataFormat': 'application/json'
#             }
#         },
#         "savePath": {"value": "sample2.pdf", "type": "String"}
#     }