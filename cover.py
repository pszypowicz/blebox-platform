"""Support for BleBox covers."""
from homeassistant.components.cover import (
    ATTR_POSITION,
    DEVICE_CLASS_SHUTTER,
    STATE_CLOSED,
    STATE_CLOSING,
    STATE_OPEN,
    STATE_OPENING,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_STOP,
    SUPPORT_SET_POSITION,
    CoverDevice,
)

import requests

from . import DOMAIN

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    add_entities([BleBoxCover(name,ip) for name,ip in hass.data[DOMAIN]['shutters'].items()])


class BleBoxCover(CoverDevice):
    """Representation of a blebox cover.
    Current shutter state. Where: 0 - Moving down, 1 - Moving up, 2 - Manually stopped, 3 - Lower limit, 4 - Upper limit.
    """

    def __init__(self,name,ip):
        """Initialize the sensor."""
        self._name = name
        self._ip = ip
        self._state = None
        self._ext = None
        self._position = None

    def command(self,command,parameter=None):
        if command == "p":
            r = requests.get(f"http://{self._ip}/s/{command}/{100-parameter}")
        else:
            r = requests.get(f"http://{self._ip}/s/{command}")
        return r.json

    @property
    def device_class(self):
        return DEVICE_CLASS_SHUTTER

    @property
    def current_cover_position(self):
        return self._position

    @property
    def is_opening(self):
        return self._state == STATE_OPENING

    @property
    def is_closing(self):
        return self._state == STATE_CLOSING

    @property
    def is_closed(self):
        return self._state == STATE_CLOSED

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    async def async_update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        r = requests.get(f"http://{self._ip}/api/shutter/extended/state")
        ext = r.json()

        self._position = 100 - ext['shutter']['currentPos']['position']

        if ext['shutter']['state'] == 1:
            self._state = STATE_OPENING
        elif ext['shutter']['state'] == 0:
            self._state = STATE_CLOSING
        elif ext['shutter']['state'] == 3:
            self._state = STATE_CLOSED

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        self.command("u")

    async def async_close_cover(self, **kwargs):
        """Close cover."""
        self.command("d")

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        self.command("p",kwargs[ATTR_POSITION])

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        self.command("s")

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_SET_POSITION | SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_STOP