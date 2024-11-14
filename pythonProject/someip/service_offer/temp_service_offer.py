import asyncio
import ipaddress
import random
from someipy import (
    EventGroup,
    ServiceBuilder,
    construct_server_service_instance,
    TransportLayerProtocol
)
from someipy.service_discovery import construct_service_discovery
from someip.dataclasses.dataclasses import Temperature
from someipy.serialization import Uint8, Uint64

sd_multicast_group = "224.224.224.245"
sd_port = 30490
interface_ip = "127.0.0.3"
instance_id = 0x5678
sample_service_id = 0x1234
sample_eventgroup_id = 0x0321
event_ids = [32769, 32770, 32771]

def create_temperature_message(msg: Temperature):
    msg.measurement.value = random.randint(20, 60)
    msg.timestamp = Uint64(msg.timestamp.value + 1)
    return msg

async def setup_service_discovery():
    return await construct_service_discovery(sd_multicast_group, sd_port, interface_ip)

async def setup_server_service(service_discovery):
    temperature_eventgroup = EventGroup(
        id=sample_eventgroup_id, event_ids=event_ids
    )
    temperature_service = (
        ServiceBuilder()
        .with_service_id(sample_service_id)
        .with_major_version(1)
        .with_eventgroup(temperature_eventgroup)
        .build()
    )

    service_instance = await construct_server_service_instance(
        temperature_service,
        instance_id=instance_id,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3000),
        ttl=5,
        sd_sender=service_discovery,
        cyclic_offer_delay_ms=2000,
        protocol=TransportLayerProtocol.UDP,
    )

    service_instance.start_offer()
    service_discovery.attach(service_instance)
    return service_instance

async def main_send():
    service_discovery = await setup_service_discovery()
    service_instance = await setup_server_service(service_discovery)
    msg = Temperature()
    msg.version.major = Uint8(1)
    msg.version.minor = Uint8(0)
    try:
        while True:
            await asyncio.sleep(1)
            temperature_msg = create_temperature_message(msg)
            payload = temperature_msg.serialize()
            service_instance.send_event(
                sample_eventgroup_id, event_ids[0], payload
            )
    except asyncio.CancelledError:
        print("Stopping service offer...")
        await service_instance.stop_offer()
    finally:
        service_discovery.close()

if __name__ == "__main__":
    asyncio.run(main_send())
