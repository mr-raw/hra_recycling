# integration_blueprint

[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]




## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `integration_blueprint`.
4. Download _all_ the files from the `custom_components/integration_blueprint/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Integration blueprint"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/integration_blueprint/translations/en.json
custom_components/integration_blueprint/translations/nb.json
custom_components/integration_blueprint/__init__.py
custom_components/integration_blueprint/api.py
custom_components/integration_blueprint/config_flow.py
custom_components/integration_blueprint/const.py
custom_components/integration_blueprint/entity.py
custom_components/integration_blueprint/manifest.json
custom_components/integration_blueprint/sensor.py

```

## Configuration is done in the UI

[hra_recycle]: https://github.com/mr-raw/hra_recycling
[buymecoffee]: https://www.buymeacoffee.com/erikraae
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
