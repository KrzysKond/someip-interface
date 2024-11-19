
import ipaddress
import logging

from someipy import (
    construct_client_service_instance,
    TransportLayerProtocol,
    service_discovery,
    ServiceBuilder
)
from someipy.logging import set_someipy_log_level


async def construct_service_instances():
    interface_ip = "127.0.0.1"
    service_instances = []

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
    envservice_instances.append(newtempevent_1_instance)

    newtempevent_2_instance = await construct_client_service_instance(
        service=envservice,
        instance_id=32770,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    envservice_instances.append(newtempevent_2_instance)

    newtempevent_3_instance = await construct_client_service_instance(
        service=envservice,
        instance_id=32771,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    envservice_instances.append(newtempevent_3_instance)

    newpressevent_instance = await construct_client_service_instance(
        service=envservice,
        instance_id=32773,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    envservice_instances.append(newpressevent_instance)

    newdpressevent_instance = await construct_client_service_instance(
        service=envservice,
        instance_id=32771,
        endpoint=(ipaddress.IPv4Address(interface_ip), 3002),
        ttl=5,
        sd_sender=service_discovery,
        protocol=TransportLayerProtocol.UDP,
    )
    envservice_instances.append(newdpressevent_instance)

    for instance in service_instances:
        service_discovery.attach(instance)

async def main():
    await construct_service_instances()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
