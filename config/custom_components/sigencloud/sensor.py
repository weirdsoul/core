"""Platform for sensor integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SigenCloud sensors from a config entry."""

    # 1. Get any data you saved during the config flow
    # username = config_entry.data.get("username")

    # 2. Initialize your sensors
    new_devices = [SigenSensor(config_entry.runtime_data)]

    # 3. Add the sensors to Home Assistant
    async_add_entities(new_devices)


class SigenSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True
    _attr_name = "Load power"
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    # TODO: Set a unique ID for the sensor, e.g. serial number or MAC address
    _attr_unique_id = "load_power"

    def __init__(self, sigen_instance) -> None:
        """Initialize the sensor."""
        self._sigen = sigen_instance

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, "example_device")},
            name="Sigen Inverter",
            manufacturer="Sigenergy",
        )

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        energy_flow = await self._sigen.get_energy_flow()
        self._attr_native_value = energy_flow["loadPower"]
