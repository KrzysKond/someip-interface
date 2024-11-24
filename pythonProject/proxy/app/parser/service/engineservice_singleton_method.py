
import ipaddress
import logging
import asyncio
from asyncio import timeout
from inspect import stack

from someipy import (
    construct_client_service_instance,
    TransportLayerProtocol,
    ServiceBuilder, SomeIpMessage, MethodResult
)
from someipy.logging import set_someipy_log_level
from someipy.service_discovery import construct_service_discovery

from proxy.app.parser.service.engineservice import Start
from proxy.app.settings import INTERFACE_IP, MULTICAST_GROUP, SD_PORT
from proxy.app.parser.dataclass.engineservice_dataclass import CurrentModeMsg
from proxy.app.parser.dataclass.engineservice_dataclass import StartMsg
from proxy.app.parser.dataclass.engineservice_dataclass import SetModeMsg
from proxy.app.someip.mock_offer.addition_method_parameters import Sum, Addends

SAMPLE_SERVICE_ID = 0x1234
SAMPLE_INSTANCE_ID = 0x5678
SAMPLE_METHOD_ID = 0x0123

class ServiceManagerSingleton:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(ServiceManagerSingleton, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.service_discovery = None
        self.methods = []
        self.events = []
        self.start_instance = None
        self.setmode_instance = None
        self.engineservice  = None

        self.engineservice
    async def setup_service_discovery(self):
        if not self.service_discovery:
            self.service_discovery = await construct_service_discovery(MULTICAST_GROUP, SD_PORT, INTERFACE_IP)
        return self.service_discovery

    async def setup_manager(self) -> None:

        self.engineservice = (
            ServiceBuilder()
            .with_service_id(SAMPLE_SERVICE_ID)
            .with_major_version(1)
            .build()
        )



        self.setmode_instance = await construct_client_service_instance(
            service=self.engineservice,
            instance_id=2,
            endpoint=(ipaddress.IPv4Address(INTERFACE_IP), 3002),
            ttl=5,
            sd_sender=self.service_discovery,
            protocol=TransportLayerProtocol.UDP,
        )
        self.methods.append(self.setmode_instance)
        self.service_discovery.attach(self.setmode_instance)


        self.start_instance = await construct_client_service_instance(
            service=self.engineservice,
            instance_id=SAMPLE_INSTANCE_ID,
            endpoint=(ipaddress.IPv4Address(INTERFACE_IP), 3002),
            ttl=5,
            sd_sender=self.service_discovery,
            protocol=TransportLayerProtocol.UDP,
        )
        self.methods.append(self.start_instance)
        self.service_discovery.attach(self.start_instance)

        self.currentmode_instance = await construct_client_service_instance(
            service=self.engineservice,
            instance_id=32769,
            endpoint=(ipaddress.IPv4Address(INTERFACE_IP), 3002),
            ttl=5,
            sd_sender=self.service_discovery,
            protocol=TransportLayerProtocol.UDP,
        )
        self.currentmode_instance.register_callback(self.callback_currentmode_msg)
        self.currentmode_instance.subscribe_eventgroup(32769)
        self.events.append(self.currentmode_instance)
      #  self.service_discovery.attach(self.currentmode_instance)




    def callback_currentmode_msg(self, someip_message: SomeIpMessage) -> None:
        try:
            print(f"Received {len(someip_message.payload)} bytes for event {someip_message.header.method_id}. Attempting deserialization...")
            CurrentMode_msg = CurrentModeMsg().deserialize(someip_message.payload)
            print(CurrentMode_msg)
        except Exception as e:
            print(f"Error in deserialization: {e}")

    async def Start(self, start):
        try:
            self.start_instance = self.start_instance
            self.service_discovery.attach(self.start_instance)

            while True:
                method_parameter = Addends(addend1=1, addend2=2)
                method_success, method_result = await self.start_instance.call_method(
                    SAMPLE_METHOD_ID, method_parameter.serialize()
                )
                if method_success == MethodResult.SUCCESS:
                    print(
                        f"Received result for method: {' '.join(f'0x{b:02x}' for b in method_result)}"
                    )
                    try:
                        sum = Sum().deserialize(method_result)
                        print(f"Sum: {sum.value.value}")
                    except Exception as e:
                        print(f"Error during deserialization of method's result: {e}")
                elif method_success == MethodResult.ERROR:
                    print("Method call failed..")
                elif method_success == MethodResult.TIMEOUT:
                    print("Method call timed out..")
                elif method_success == MethodResult.SERVICE_NOT_FOUND:
                    print("Service not yet available..")

                await asyncio.sleep(2)
        except Exception as e:
            print(f"Error in Start method: {e}")


    async def SetMode(self, setmode):
        method_result = await self.setmode_instance.call_method(
            2, SetModeMsg().serialize()
        )
        return method_result

    async def shutdown(self):
        if self.service_discovery:
            self.service_discovery.close()
        for event in self.events:
            if event:
                await event.close()
        for method in self.methods:
            if method:
                await method.close()

async def main():
    set_someipy_log_level(logging.DEBUG)
    service_manager = ServiceManagerSingleton()
    await service_manager.setup_service_discovery()

    try:
        await service_manager.setup_manager()
        while True:
            await service_manager.Start(True)


    except asyncio.CancelledError:
        print("Shutdown..")



if __name__ == "__main__":
    asyncio.run(main())
