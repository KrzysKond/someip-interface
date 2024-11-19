import json
from typing import Dict, Any

from proxy.app.settings import INTERFACE_IP


def load_json(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as file:
        return json.load(file)

def generate_service_code(parsed_config, interface_ip, port=3002, ttl=5):
    services = parsed_config['someip']
    service_code = f"""
import ipaddress
from someipy import (
    construct_client_service_instance,
    TransportLayerProtocol,
    service_discovery,
    ServiceBuilder
)

async def construct_service_instances():
    interface_ip = "{interface_ip}"
    service_instances = []
"""

    for service_name, service_config in services.items():
        service_id = service_config['service_id']
        major_version = service_config['major_version']
        methods = service_config.get('methods', {})
        events = service_config.get('events', {})

        service_variable_name = f"{service_name.lower()}"

        service_code += f"""
    {service_variable_name}_instances = []
    {service_variable_name}= (
        ServiceBuilder()
        .with_service_id({service_id})
        .with_major_version({major_version})
        .build()
        )
"""

        for method_name, method_config in methods.items():
            instance_id = method_config['id']
            service_code += f"""
    {method_name.lower()}_instance = await construct_client_service_instance(
        service={service_variable_name},
        instance_id={instance_id},
        endpoint=(ipaddress.IPv4Address(interface_ip), {port}),
        ttl={ttl},
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    {service_variable_name}_instances.append({method_name.lower()}_instance)
"""

        for event_name, event_config in events.items():
            instance_id = event_config['id']
            service_code += f"""
    {event_name.lower()}_instance = await construct_client_service_instance(
        service={service_variable_name.lower()},
        instance_id={instance_id},
        endpoint=(ipaddress.IPv4Address(interface_ip), {port}),
        ttl={ttl},
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    {service_variable_name}_instances.append({event_name.lower()}_instance)
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
    save_code(f'service/{service_variable_name}.py', service_code)
    return service_code

def save_code(file_path: str, code: str):
    with open(file_path, "w") as file:
        file.write(code)

def process_service_json(input_json_path: str, interface_ip: str):
    parsed_config = load_json(input_json_path)
    generate_service_code(parsed_config, interface_ip)


input_json_path = 'input/env_service.json'
interface_ip = INTERFACE_IP

process_service_json(input_json_path, interface_ip)
