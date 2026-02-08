"""Platform for sensor integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SigenConfigEntry, SigenDataUpdateCoordinator
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SigenConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SigenCloud sensors from a config entry."""

    coordinator = entry.runtime_data

    new_devices = [
        SigenEnergySensor(coordinator, "pvDayNrg", "Total PV Energy"),
        SigenPowerSensor(coordinator, "pvPower", "Current PV Power"),
        SigenPowerSensor(coordinator, "loadPower", "Current Load Power"),
        SigenPowerSensor(coordinator, "buySellPower", "Grid Import/Export Power"),
    ]

    async_add_entities(new_devices)


class SigenEntity(CoordinatorEntity[SigenDataUpdateCoordinator]):
    """Base class for Sigen entities."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: SigenDataUpdateCoordinator, key: str, name: str
    ) -> None:
        """Initialize the Sigen entity."""
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{key}"
        self._attr_name = name

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._key)},
            name="Sigen Inverter",  # This will be refined later
            manufacturer="Sigenergy",
        )

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self.coordinator.data[self._key]


class SigenPowerSensor(SigenEntity, SensorEntity):
    """Representation of a Sigen Power Sensor."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_state_class = SensorStateClass.MEASUREMENT


class SigenEnergySensor(SigenEntity, SensorEntity):
    """Representation of a Sigen Energy Sensor."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
