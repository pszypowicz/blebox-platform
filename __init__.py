"""[WIP] verion of blebox integration"""
DOMAIN = 'blebox'

def setup(hass, config):
    hass.data[DOMAIN] = {
        'shutters': {
            'Cover 1': '192.168.X.X',
            'Cover 2': '192.168.X.XZ'
        }
    }

    hass.helpers.discovery.load_platform('cover', DOMAIN, {}, config)

    return True
