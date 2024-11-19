
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

from proxy.app.parser.dataclass.envservice_dataclass import newTempEvent_1Msg
from proxy.app.parser.dataclass.envservice_dataclass import newTempEvent_2Msg
from proxy.app.parser.dataclass.envservice_dataclass import newTempEvent_3Msg
from proxy.app.parser.dataclass.envservice_dataclass import newPressEventMsg
from proxy.app.parser.dataclass.envservice_dataclass import newDPressEventMsg
            
def callback_newtempevent_1_msg(someip_message: SomeIpMessage) -> None:
    try:
        print(f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization...")
        newTempEvent_1_msg = newTempEvent_1Msg().deserialize(someip_message.payload)
        print(newTempEvent_1_msg)
    except Exception as e:
        print(f"Error in deserialization: {e}")

            
def callback_newtempevent_2_msg(someip_message: SomeIpMessage) -> None:
    try:
        print(f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization...")
        newTempEvent_2_msg = newTempEvent_2Msg().deserialize(someip_message.payload)
        print(newTempEvent_2_msg)
    except Exception as e:
        print(f"Error in deserialization: {e}")

            
def callback_newtempevent_3_msg(someip_message: SomeIpMessage) -> None:
    try:
        print(f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization...")
        newTempEvent_3_msg = newTempEvent_3Msg().deserialize(someip_message.payload)
        print(newTempEvent_3_msg)
    except Exception as e:
        print(f"Error in deserialization: {e}")

            
def callback_newpressevent_msg(someip_message: SomeIpMessage) -> None:
    try:
        print(f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization...")
        newPressEvent_msg = newPressEventMsg().deserialize(someip_message.payload)
        print(newPressEvent_msg)
    except Exception as e:
        print(f"Error in deserialization: {e}")

            
def callback_newdpressevent_msg(someip_message: SomeIpMessage) -> None:
    try:
        print(f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization...")
        newDPressEvent_msg = newDPressEventMsg().deserialize(someip_message.payload)
        print(newDPressEvent_msg)
    except Exception as e:
        print(f"Error in deserialization: {e}")

async def setup_service_discovery():
    return await construct_service_discovery(MULTICAST_GROUP, SD_PORT, INTERFACE_IP)

async def construct_service_instances(service_discovery):
    interface_ip = "127.0.0.1"

    envservice_instances = []

    envservice= (
        ServiceBuilder()
        .with_service_id(514)
        .with_major_version(1)
        .build()
        )

    newtempevent_1_instance = await construct_client_service_instance(
        service=envservice,
        instance_id=32769,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    newtempevent_1_instance.register_callback(callback_newtempevent_1_msg)
    newtempevent_1_instance.subscribe_eventgroup(32769)
    envservice_instances.append(newtempevent_1_instance)

    newtempevent_2_instance = await construct_client_service_instance(
        service=envservice,
        instance_id=32770,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    newtempevent_2_instance.register_callback(callback_newtempevent_2_msg)
    newtempevent_2_instance.subscribe_eventgroup(32770)
    envservice_instances.append(newtempevent_2_instance)

    newtempevent_3_instance = await construct_client_service_instance(
        service=envservice,
        instance_id=32771,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    newtempevent_3_instance.register_callback(callback_newtempevent_3_msg)
    newtempevent_3_instance.subscribe_eventgroup(32771)
    envservice_instances.append(newtempevent_3_instance)

    newpressevent_instance = await construct_client_service_instance(
        service=envservice,
        instance_id=32773,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    newpressevent_instance.register_callback(callback_newpressevent_msg)
    newpressevent_instance.subscribe_eventgroup(32773)
    envservice_instances.append(newpressevent_instance)

    newdpressevent_instance = await construct_client_service_instance(
        service=envservice,
        instance_id=32771,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    newdpressevent_instance.register_callback(callback_newdpressevent_msg)
    newdpressevent_instance.subscribe_eventgroup(32771)
    envservice_instances.append(newdpressevent_instance)

    for instance in envservice_instances:
        service_discovery.attach(instance)
    return envservice_instances

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
