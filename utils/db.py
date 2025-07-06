import json

def load(file_name):
    with open(f"data/{file_name}", "r") as file:
        data = json.load(file)
    return data

def save(file_name, data):
    with open(f"data/{file_name}", "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return True