import asyncio
from someipy.service_discovery import construct_service_discovery

from proxy.app.settings import INTERFACE_IP, MULTICAST_GROUP, SD_PORT


async def setup_service_discovery():
    return await construct_service_discovery(MULTICAST_GROUP, SD_PORT, INTERFACE_IP)



if __name__ == "__main__":

    asyncio.run(setup_service_discovery())