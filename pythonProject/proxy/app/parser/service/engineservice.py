import logging
import ipaddress
from someipy import (
    construct_client_service_instance,
    TransportLayerProtocol,
    ServiceBuilder, SomeIpMessage
)
from someipy.logging import set_someipy_log_level
from someipy.service_discovery import construct_service_discovery

from proxy.app.parser.dataclass.engineservice_dataclass import CurrentModeMsg
from proxy.app.settings import INTERFACE_IP, MULTICAST_GROUP, SD_PORT
from proxy.app.someip.mock_offer.current_mode_engine_offer import sample_eventgroup_id

sample_service_id = 518
sample_event_group_id = 32769
sample_instance_id = 32769

def callback_example(someip_message : SomeIpMessage) -> None:
    try:
        print("miau")
        print(
            f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization..."
        )
        current_mode_msg = CurrentModeMsg().deserialize(someip_message.payload)
        print(current_mode_msg)
    except Exception as e:
        print(f"Error in deserialization: {e}")



async def setup_service_discovery():
    return await construct_service_discovery(MULTICAST_GROUP, SD_PORT, INTERFACE_IP)

async def construct_service_instances(service_discovery):
    interface_ip = "127.0.0.1"
    engineservice= (
        ServiceBuilder()
        .with_service_id(sample_service_id)
        .with_major_version(1)
        .build()
        )

    currentmode_instance = await construct_client_service_instance(
        service=engineservice,
        instance_id=sample_instance_id,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    currentmode_instance.register_callback(callback_example)
    currentmode_instance.subscribe_eventgroup(sample_eventgroup_id)


    return currentmode_instance


async def main():
    set_someipy_log_level(logging.DEBUG)
    service_discovery = await setup_service_discovery()
    service_instance = await construct_service_instances(service_discovery)
    service_discovery.attach(service_instance)
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Shutting down...")
    finally:
        service_discovery.close()
        await service_instance.close()



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
