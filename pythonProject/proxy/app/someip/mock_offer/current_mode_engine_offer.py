import asyncio
import ipaddress
import random

from someipy import ServiceBuilder, EventGroup, construct_server_service_instance, TransportLayerProtocol
from someipy.serialization import Uint8
from someipy.service_discovery import construct_service_discovery

from proxy.app.parser.dataclass.engineservice_dataclass import CurrentModeMsg


sd_multicast_group = "224.224.224.245"
sd_port = 30490
interface_ip = "127.0.0.2"
instance_id = 32769
sample_service_id = 0x1234
sample_eventgroup_id = 32769
event_ids = [32769]

async def setup_service_discovery():
    return await construct_service_discovery(sd_multicast_group, sd_port, interface_ip)

def create_temperature_message(msg: CurrentModeMsg):
    msg.out = Uint8(random.randint(1, 20))
    return msg


async def setup_server_service(service_discovery):
    engine_eventgroup = EventGroup(
        id=sample_eventgroup_id, event_ids=event_ids
    )
    engineservice = (
        ServiceBuilder()
        .with_service_id(518)
        .with_major_version(1)
        .build()
    )

    service_instance = await construct_server_service_instance(
        engineservice,
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
    msg = CurrentModeMsg()
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