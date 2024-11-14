import json
from typing import Any, Dict


# Helper function to generate type hints
def map_json_type(json_type: str) -> str:
    type_mapping = {
        "uint8": "int",
        "bool": "bool",
        "void": "None",
        "int16": "int",
        "int32": "int",
        "int64": "int",
        "float32": "float",
        "float64": "float",
        "string": "str"
    }
    return type_mapping.get(json_type, "Any")


# Function to generate dataclass for a single method
def generate_method_dataclass(method_name: str, method_info: Dict[str, Any]) -> str:
    class_name = f"{method_name}Request"

    input_data = method_info.get("data_structure", {}).get("in", {})
    input_type = input_data.get("type", "void")

    if input_type == "void":
        in_field = "    pass"
    else:
        input_name = input_data.get("name", "value")
        in_field = f"    {input_name}: {map_json_type(input_type)}"

    class_definition = f"""
@dataclass
class {class_name}:
{in_field}
"""
    return class_definition


# Function to generate event dataclass
def generate_event_dataclass(event_name: str, event_info: Dict[str, Any]) -> str:
    class_name = f"{event_name}Event"

    output_data = event_info.get("data_structure", {}).get("out", {})
    output_type = output_data.get("type", "Any")

    class_definition = f"""
@dataclass
class {class_name}:
    data: {map_json_type(output_type)}
"""
    return class_definition


# Main generation function
def generate_dataclasses(json_data: Dict[str, Any]) -> str:
    package = json_data.get("package", "generated")
    someip_services = json_data.get("../someip", {})

    result = [
        "from dataclasses import dataclass",  # Import statement
        f"# Package: {package}"
    ]

    for service_name, service_info in someip_services.items():
        result.append(f"# Service: {service_name}")

        # Generate methods
        for method_name, method_info in service_info.get("methods", {}).items():
            class_def = generate_method_dataclass(method_name, method_info)
            result.append(class_def)

        # Generate events
        for event_name, event_info in service_info.get("events", {}).items():
            event_def = generate_event_dataclass(event_name, event_info)
            result.append(event_def)

    return "\n".join(result)


# Read JSON from a file
def read_json_file(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return {}


# Main execution
if __name__ == "__main__":
    input_file = "service.json"  # Replace with your input file path
    json_data = read_json_file(input_file)

    if json_data:
        dataclass_code = generate_dataclasses(json_data)

        # Output the generated dataclasses
        output_file = "output.py"  # Save the output to a file
        with open(output_file, "w") as file:
            file.write(dataclass_code)

        print(f"Dataclasses generated and saved to {output_file}")
    else:
        print("Failed to generate dataclasses due to input errors.")
