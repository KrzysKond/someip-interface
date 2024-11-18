from platform import version
from typing import dataclass_transform

from dataclasses import dataclass

from someipy.serialization import (
    SomeIpPayload,
    Uint8, Uint64
)

@dataclass
class Version(SomeIpPayload):
        major: Uint8
        minor: Uint8

        def __init__(self):
            self.major = Uint8()
            self.minor = Uint8()

@dataclass
class TemperatureMsg(SomeIpPayload):
    version: Version
    measurement: Uint8
    timestamp: Uint64

    def __init__(self):
        self.measurement = Uint8()
        self.version = Version()
        self.timestamp = Uint64(0)

