"""The Sigen Cloud API integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from sigen import Sigen

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.SENSOR]

DOMAIN = "sigencloud"
UPDATE_INTERVAL = timedelta(seconds=30)


class SigenDataUpdateCoordinator(DataUpdateCoordinator[dict[str, float]]):
    """Class to manage fetching Sigen data."""

    def __init__(self, hass: HomeAssistant, sigen_client: Sigen) -> None:
        """Initialize."""
        self.sigen = sigen_client
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, float]:
        """Update data via library."""
        try:
            return await self.sigen.get_energy_flow()
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with Sigen Cloud API: {err}"
            ) from err


type SigenConfigEntry = ConfigEntry[SigenDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: SigenConfigEntry) -> bool:
    """Set up Sigen Cloud API from a config entry."""

    sigen_client = Sigen(
        entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], entry.data[CONF_REGION]
    )
    await sigen_client.async_initialize()

    coordinator = SigenDataUpdateCoordinator(hass, sigen_client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: SigenConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
