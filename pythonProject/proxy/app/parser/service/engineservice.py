import logging
import ipaddress
from someipy import (
    construct_client_service_instance,
    TransportLayerProtocol,
    ServiceBuilder, SomeIpMessage
)
from someipy.logging import set_someipy_log_level

from proxy.app.parser.dataclass.engineservice_dataclass import CurrentModeMsg
from proxy.app.someip.setup import setup_service_discovery


def callback_example(someip_message : SomeIpMessage) -> None:
    print(
        f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization..."
    )
    current_mode_msg = CurrentModeMsg.deserialize(someip_message.payload)
    print(current_mode_msg)


async def construct_service_instances(service_discovery):
    interface_ip = "127.0.0.1"
    service_instances = []

    engineservice_instances = []
    engineservice= (
        ServiceBuilder()
        .with_service_id(518)
        .with_major_version(1)
        .build()
        )

    start_instance = await construct_client_service_instance(
        service=engineservice,
        instance_id=1,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    engineservice_instances.append(start_instance)

    setmode_instance = await construct_client_service_instance(
        service=engineservice,
        instance_id=2,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    engineservice_instances.append(setmode_instance)

    currentmode_instance = await construct_client_service_instance(
        service=engineservice,
        instance_id=32769,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    currentmode_instance.register_callback(callback_example)
    currentmode_instance.subscribe_eventgroup(32769)
    engineservice_instances.append(currentmode_instance)


    return service_instances


async def main():
    set_someipy_log_level(logging.DEBUG)
    service_discovery = await setup_service_discovery()
    service_instances = await construct_service_instances(service_discovery)
    for instance in service_instances:
        service_discovery.attach(instance)

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Shutting down...")
    finally:
        service_discovery.close()
        for instance in service_instances:
            instance.close()



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
