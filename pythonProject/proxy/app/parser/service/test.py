import asyncio
import ipaddress
import logging
from someipy import construct_client_service_instance, TransportLayerProtocol, ServiceBuilder, SomeIpMessage
from someipy.logging import set_someipy_log_level
from someipy.service_discovery import construct_service_discovery

from proxy.app.parser.dataclass.engineservice_dataclass import CurrentModeMsg
from proxy.app.settings import INTERFACE_IP, MULTICAST_GROUP, SD_PORT


async def setup_service_discovery():
    return await construct_service_discovery(MULTICAST_GROUP, SD_PORT, INTERFACE_IP)


async def create_currentmode_instance(service_discovery) :
    engineservice = (
        ServiceBuilder()
        .with_service_id(518)
        .with_major_version(1)
        .build()
    )

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

    return currentmode_instance


def callback_currentmode_msg(someip_message: SomeIpMessage) -> None:
    try:
        print(
            f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization...")
        currentmode_msg = CurrentModeMsg().deserialize(someip_message.payload)
        print(currentmode_msg)
    except Exception as e:
        print(f"Error in deserialization: {e}")


async def main():
    set_someipy_log_level(logging.DEBUG)
    service_discovery = await setup_service_discovery()
    service = await create_currentmode_instance(service_discovery)
    service_discovery.attach(service)
    try:
        await asyncio.Future()
    except Exception as e:
        print(e)



if __name__ == "__main__":
    asyncio.run(main())