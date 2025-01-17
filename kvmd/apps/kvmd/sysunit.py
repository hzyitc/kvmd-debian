# ========================================================================== #
#                                                                            #
#    KVMD - The main PiKVM daemon.                                           #
#                                                                            #
#    Copyright (C) 2018-2022  Maxim Devaev <mdevaev@gmail.com>               #
#                                                                            #
#    This program is free software: you can redistribute it and/or modify    #
#    it under the terms of the GNU General Public License as published by    #
#    the Free Software Foundation, either version 3 of the License, or       #
#    (at your option) any later version.                                     #
#                                                                            #
#    This program is distributed in the hope that it will be useful,         #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#    GNU General Public License for more details.                            #
#                                                                            #
#    You should have received a copy of the GNU General Public License       #
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.  #
#                                                                            #
# ========================================================================== #


import types

from typing import Tuple
from typing import Type
from typing import Optional

import dbus
import dbus.exceptions

from ... import aiotools


# =====
class SystemdUnitInfo:
    def __init__(self) -> None:
        self.__bus: Optional[dbus.SystemBus] = None
        self.__manager: Optional[dbus.Interface] = None

    async def get_status(self, name: str) -> Tuple[bool, bool]:
        assert self.__bus is not None
        assert self.__manager is not None

        if not name.endswith(".service"):
            name += ".service"

        return await aiotools.run_async(self.__inner_get_status, name)

    def __inner_get_status(self, name: str) -> Tuple[bool, bool]:
        try:
            unit_p = self.__manager.GetUnit(name)
            unit = self.__bus.get_object("org.freedesktop.systemd1", unit_p)
            unit_props = dbus.Interface(unit, dbus_interface="org.freedesktop.DBus.Properties")
            started = (unit_props.Get("org.freedesktop.systemd1.Unit", "ActiveState") == "active")
        except dbus.exceptions.DBusException as err:
            if "NoSuchUnit" not in str(err):
                raise
            started = False
        enabled = (self.__manager.GetUnitFileState(name) in [
            "enabled",
            "enabled-runtime",
            "static",
            "indirect",
            "generated",
        ])
        return (enabled, started)

    async def open(self) -> None:
        await aiotools.run_async(self.__inner_open)

    def __inner_open(self) -> None:
        self.__bus = dbus.SystemBus()
        systemd = self.__bus.get_object("org.freedesktop.systemd1", "/org/freedesktop/systemd1")
        self.__manager = dbus.Interface(systemd, dbus_interface="org.freedesktop.systemd1.Manager")

    async def __aenter__(self) -> "SystemdUnitInfo":
        await self.open()
        return self

    async def close(self) -> None:
        try:
            if self.__bus is not None:
                await aiotools.run_async(self.__bus.close)
        except Exception:
            pass
        self.__manager = None
        self.__bus = None

    async def __aexit__(
        self,
        _exc_type: Type[BaseException],
        _exc: BaseException,
        _tb: types.TracebackType,
    ) -> None:

        await self.close()
