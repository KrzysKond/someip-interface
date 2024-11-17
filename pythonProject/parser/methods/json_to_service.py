import ipaddress
import json
from typing import Dict, Any
from someipy import (
    construct_client_service_instance,
    TransportLayerProtocol,
    service_discovery,
    ServiceBuilder
)

def load_json(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as file:
        return json.load(file)

def generate_service_code(parsed_config, interface_ip, port=3002, ttl=5):
    service_id = parsed_config['someip']['EngineService']['service_id']
    major_version = parsed_config['someip']['EngineService']['major_version']
    methods = parsed_config['someip']['EngineService'].get('methods', {})
    events = parsed_config['someip']['EngineService'].get('events', {})

    service_code = f"""
import ipaddress
from someipy import (
    construct_client_service_instance,
    TransportLayerProtocol,
    service_discovery,
    ServiceBuilder
)

async def construct_service_instances():
    service_id = {service_id}
    major_version = {major_version}
    interface_ip = "{interface_ip}"

    engine_service = ServiceBuilder().with_service_id(service_id).with_major_version(major_version).build()
    service_instances = []

"""

    for method_name, method_config in methods.items():
        instance_id = method_config['id']
        service_code += f"""
    {method_name.lower()}_instance = await construct_client_service_instance(
        service=engine_service,
        instance_id={instance_id},
        endpoint=(ipaddress.IPv4Address(interface_ip), {port}),
        ttl={ttl},
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    service_instances.append({method_name.lower()}_instance)
"""

    for event_name, event_config in events.items():
        instance_id = event_config['id']
        service_code += f"""
    {event_name.lower()}_instance = await construct_client_service_instance(
        service=engine_service,
        instance_id={instance_id},
        endpoint=(ipaddress.IPv4Address(interface_ip), {port}),
        ttl={ttl},
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    service_instances.append({event_name.lower()}_instance)
"""

    service_code += """
    for instance in service_instances:
        service_discovery.attach(instance)

async def main():
    await construct_service_instances()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
"""

    return service_code

def save_code(file_path: str, code: str):
    with open(file_path, "w") as file:
        file.write(code)

def process_service_json(input_json_path: str, output_code_path: str, interface_ip: str):
    parsed_config = load_json(input_json_path)
    generated_service_code = generate_service_code(parsed_config, interface_ip)
    save_code(output_code_path, generated_service_code)

input_json_path = '../input_structure_engine.json'
output_code_path = 'generated_service.py'
interface_ip = "10.101.0.1"

process_service_json(input_json_path, output_code_path, interface_ip)
