"""Platform for sensor integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower
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
        SigenEnergySensor(coordinator, entry, "pvDayNrg", "Total PV Energy"),
        SigenPowerSensor(coordinator, entry, "pvPower", "Current PV Power"),
        SigenPowerSensor(coordinator, entry, "loadPower", "Current Load Power"),
        SigenPowerSensor(
            coordinator, entry, "buySellPower", "Grid Import/Export Power"
        ),
        SigenPowerSensor(coordinator, entry, "batteryPower", "Battery Power"),
        SigenBatterySensor(coordinator, entry, "batterySoc", "Battery SOC"),
    ]

    async_add_entities(new_devices)


class SigenEntity(CoordinatorEntity[SigenDataUpdateCoordinator]):
    """Base class for Sigen entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SigenDataUpdateCoordinator,
        entry: SigenConfigEntry,
        key: str,
        name: str,
    ) -> None:
        """Initialize the Sigen entity."""
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}-{key}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Sigenergy",
            model="Sigen Inverter",
        )

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data:
            return None

        # Data might be a list of devices, we assume we need the first one
        if isinstance(data, list):
            if not data:
                return None
            data = data[0]

        value = None
        if isinstance(data, dict):
            value = data.get(self._key)
        else:
            value = getattr(data, self._key, None)

        if value is None:
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None


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


class SigenBatterySensor(SigenEntity, SensorEntity):
    """Representation of a Sigen Battery Sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
