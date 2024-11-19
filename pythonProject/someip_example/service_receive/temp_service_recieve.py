import asyncio
import json
import logging
import ipaddress
from someipy import SomeIpMessage, ServiceBuilder, TransportLayerProtocol
from someipy.logging import set_someipy_log_level
from someipy.serialization import Uint8, Uint64, SomeIpPayload
from someipy.service_discovery import construct_service_discovery
from someipy.client_service_instance import construct_client_service_instance

from someip.api.send_json_data import send_json_data
from someip.dataclasses.dataclasses import TemperatureMsg


remote_ip = "192.168.1.100"
remote_port = 12345

sd_multicast_group = "224.224.224.245"
sd_port = 30490
interface_ip = "127.0.0.2"
sample_service_id = 0x1234
sample_eventgroup_id = 0x0321
sample_event_id = 32769
sample_instance_id = 0x5678

def serialize_obj(obj):
    if isinstance(obj, (Uint8, Uint64)):
        return obj.value
    if isinstance(obj, SomeIpPayload):
        return {k: serialize_obj(v) for k, v in obj.__dict__.items()}
    if isinstance(obj, dict):
        return {k: serialize_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_obj(item) for item in obj]
    return obj

def temp_callback(someip_message: SomeIpMessage) -> None:
    try:
        print(
            f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization..."
        )
        temperature_msg = TemperatureMsg().deserialize(someip_message.payload)
        print(temperature_msg)
        serialized_data = serialize_obj(temperature_msg)
        with open("received_data.json", "r+") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
            existing_data.append(serialized_data)
            file.seek(0)
            json.dump(existing_data, file, indent=4)

        send_json_data(serialized_data, "127.0.0.1", 12345)
    except Exception as e:
        print(f"Error in deserialization: {e}")

async def setup_service_discovery():
    return await construct_service_discovery(sd_multicast_group, sd_port, interface_ip)

async def setup_client_service(service_discovery):
    temperature_service = (
        ServiceBuilder()
        .with_service_id(sample_service_id)
        .with_major_version(1)
        .build()
    )
    service_instance = await construct_client_service_instance(
        service=temperature_service,
        instance_id=sample_instance_id,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    service_instance.register_callback(temp_callback)
    service_instance.subscribe_eventgroup(sample_eventgroup_id)
    return service_instance

async def main_receive():
    set_someipy_log_level(logging.DEBUG)
    service_discovery = await setup_service_discovery()
    service_instance = await setup_client_service(service_discovery)
    service_discovery.attach(service_instance)
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Shutting down...")
    finally:
        service_discovery.close()
        await service_instance.close()

if __name__ == "__main__":
    asyncio.run(main_receive())
