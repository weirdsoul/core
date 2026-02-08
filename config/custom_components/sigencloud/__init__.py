"""The Sigen Cloud API integration."""

from __future__ import annotations

from sigen import Sigen

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant

# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.SENSOR]

type SigenConfigEntry = ConfigEntry[Sigen]


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: SigenConfigEntry) -> bool:
    """Set up Sigen Cloud API from a config entry."""

    sigen = Sigen(
        entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], entry.data[CONF_REGION]
    )
    await sigen.async_initialize()

    entry.runtime_data = sigen

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: SigenConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
