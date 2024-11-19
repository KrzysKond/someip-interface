
import ipaddress
import logging
from someipy import (
    construct_client_service_instance,
    TransportLayerProtocol,
    ServiceBuilder, SomeIpMessage
)
from someipy.logging import set_someipy_log_level
from someipy.service_discovery import construct_service_discovery
from proxy.app.settings import INTERFACE_IP, MULTICAST_GROUP, SD_PORT

from proxy.app.parser.dataclass.engineservice_dataclass import CurrentModeMsg
from proxy.app.parser.dataclass.engineservice_dataclass import StartMsg
from proxy.app.parser.dataclass.engineservice_dataclass import SetModeMsg

                  
def callback_currentmode_msg(someip_message: SomeIpMessage) -> None:
    try:
        print(f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization...")
        CurrentMode_msg = CurrentModeMsg().deserialize(someip_message.payload)
        print(CurrentMode_msg)
    except Exception as e:
        print(f"Error in deserialization: {e}")

async def Start(start) -> None:
    method_result = await start_instance.call_method(
        1, StartMsg().serialize()
    )
    return method_result

async def SetMode(setmode) -> None:
    method_result = await setmode_instance.call_method(
        2, SetModeMsg().serialize()
    )
    return method_result

async def setup_service_discovery():
    return await construct_service_discovery(MULTICAST_GROUP, SD_PORT, INTERFACE_IP)


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
        endpoint=(ipaddress.IPv4Address(INTERFACE_IP), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    engineservice_instances.append(start_instance)

    setmode_instance = await construct_client_service_instance(
        service=engineservice,
        instance_id=2,
        endpoint=(ipaddress.IPv4Address(INTERFACE_IP), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    engineservice_instances.append(setmode_instance)

    currentmode_instance = await construct_client_service_instance(
        service=engineservice,
        instance_id=32769,
        endpoint=(ipaddress.IPv4Address(INTERFACE_IP), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    currentmode_instance.register_callback(callback_currentmode_msg)
    currentmode_instance.subscribe_eventgroup(32769)
    engineservice_instances.append(currentmode_instance)

    for instance in engineservice_instances:
        service_discovery.attach(instance)
    return engineservice_instances


async def main():
    set_someipy_log_level(logging.DEBUG)
    service_discovery = await setup_service_discovery()
    service_instances = await construct_service_instances(service_discovery)
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Shutting down...")
    finally:
        service_discovery.close()
        for instance in service_instances:
            await instance.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
