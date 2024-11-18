
import ipaddress
from someipy import (
    construct_client_service_instance,
    TransportLayerProtocol,
    service_discovery,
    ServiceBuilder
)

async def construct_service_instances():
    interface_ip = "10.101.0.1"
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
    engineservice_instances.append(currentmode_instance)

    for instance in service_instances:
        service_discovery.attach(instance)

async def main():
    await construct_service_instances()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
