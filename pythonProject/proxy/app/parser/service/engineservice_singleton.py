
import ipaddress
import logging
import asyncio
from typing import List

from someipy import (
    construct_client_service_instance,
    TransportLayerProtocol,
    ServiceBuilder, SomeIpMessage, ClientServiceInstance
)
from someipy.logging import set_someipy_log_level
from someipy.service_discovery import construct_service_discovery
from proxy.app.settings import INTERFACE_IP, MULTICAST_GROUP, SD_PORT
from proxy.app.parser.dataclass.engineservice_dataclass import CurrentModeMsg
from proxy.app.parser.dataclass.engineservice_dataclass import StartMsg
from proxy.app.parser.dataclass.engineservice_dataclass import SetModeMsg

class ServiceManagerSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ServiceManagerSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.service_discovery = None
        self.instances = []  
        self.start_instance = None
        self.setmode_instance = None


    async def setup_service_discovery(self):
        if not self.service_discovery:
            self.service_discovery = await construct_service_discovery(MULTICAST_GROUP, SD_PORT, INTERFACE_IP)
        return self.service_discovery

    async def setup_manager(self) -> None:

        engineservice = (
            ServiceBuilder()
            .with_service_id(518)
            .with_major_version(1)
            .build()
        )

        self.start_instance = await construct_client_service_instance(
            service=engineservice,
            instance_id=1,
            endpoint=(ipaddress.IPv4Address(INTERFACE_IP), 3002),
            ttl=5,
            sd_sender=self.service_discovery,
            protocol=TransportLayerProtocol.UDP,
        )
        self.instances.append(self.start_instance) 
        self.service_discovery.attach(self.start_instance)

        self.setmode_instance = await construct_client_service_instance(
            service=engineservice,
            instance_id=2,
            endpoint=(ipaddress.IPv4Address(INTERFACE_IP), 3002),
            ttl=5,
            sd_sender=self.service_discovery,
            protocol=TransportLayerProtocol.UDP,
        )
        self.instances.append(self.setmode_instance) 
        self.service_discovery.attach(self.setmode_instance)

        currentmode_instance = await construct_client_service_instance(
            service=engineservice,
            instance_id=32769,
            endpoint=(ipaddress.IPv4Address(INTERFACE_IP), 3002),
            ttl=5,
            sd_sender=self.service_discovery,
            protocol=TransportLayerProtocol.UDP,
        )
        currentmode_instance.register_callback(self.callback_currentmode_msg)
        currentmode_instance.subscribe_eventgroup(32769)
        self.instances.append(currentmode_instance)
        self.service_discovery.attach(currentmode_instance)

    def callback_currentmode_msg(self, someip_message: SomeIpMessage) -> None:
        try:
            print(f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization...")
            CurrentMode_msg = CurrentModeMsg().deserialize(someip_message.payload)
            print(CurrentMode_msg)
        except Exception as e:
            print(f"Error in deserialization: {e}")

    async def Start(self, start) -> None:
        method_result = await self.start_instance.call_method(
            1, StartMsg().serialize()
        )
        return method_result

    async def SetMode(self, setmode) -> None:
        method_result = await self.setmode_instance.call_method(
            2, SetModeMsg().serialize()
        )
        return method_result

    async def shutdown(self):
        if self.service_discovery:
            self.service_discovery.close()
        for instance in self.instances:
            if instance:
                await instance.close()

async def main():
    set_someipy_log_level(logging.DEBUG)
    service_manager = ServiceManagerSingleton()
    await service_manager.setup_service_discovery()
    await service_manager.setup_manager()
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Shutting down...")
    finally:
        await service_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())