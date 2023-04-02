# HRA Recycling

[![buymecoffee][buymecoffeebadge]][buymecoffee]
[![validate_url][validate_badge]][validate_url]
[![Discord](https://img.shields.io/badge/Discord-mr--raw%237095-blue?logo=discord)](https://discord.com/users/303915063142776832)

## What is this?

This is a Home Assistant integration for the Norwegian waste collection company HRA (Hadeland Ringerike Avfallsselskap). You can track the pickup dates for the different fractions (Plastic, bio, glass/metal and unsorted waste)

## Installation

This integration is currently in development. Basic functionality is up and running. Please create an issue if you encounter bugs.

Version plans
- [x] 0.1.0 First release. Will have basic functionality. All the fractions will be shown. User mistakes will not be accounted for. This will break the integration and throw errors around.
- [x] 0.1.1 Small changes to the code. Did some refactoring. Using httpx instead of aiohttp.
- [ ] 1.0.0 Final release. You can choose which fractions to track. The integration has been thorougly tested.

#### Setup and configuration is done in the UI

## Examples

This example creates template sendor that shows how many days until pickup of the provided fraction:
```yaml
template:
  - sensor:
      - name: "Days Until Matavfall"
        state: >
          {% set matavfall_date = as_timestamp(states('sensor.matavfall')) %}
          {% set days_until = ((matavfall_date - as_timestamp(now())) // 86400)|round %}
          In {{ days_until }} days
```

This example sends a notification to your cellphone at 18:00 the day before the date in the provided fraction sensor:

``` yaml
automation:
  - alias: Notify the day before garbage pickup
    description: Sends a notification at 18:00 the day before the date specified in the sensor
    trigger:
      - platform: time
        at: "18:00:00"
    condition:
      - condition: template
        value_template: "{{ (as_timestamp(now()) + 86400)|timestamp_custom('%Y-%m-%d') == states('sensor.<fraction_name>') }}"
    action:
      - service: notify.<mobile_phone>
        data:
          message: "Reminder: Garbage pickup is tomorrow."
          title: "Pickup Reminder"
    mode: single

```

## Contact

If you have any questions, feel free to reach out to me on [Discord](https://discord.com/users/303915063142776832)

[hra_recycle]: https://github.com/mr-raw/hra_recycling
[buymecoffee]: https://www.buymeacoffee.com/erikraae
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg
[validate_url]: https://github.com/mr-raw/hra_recycling/actions/workflows/validate.yml
[validate_badge]: https://github.com/mr-raw/hra_recycling/actions/workflows/validate.yml/badge.svg?branch=master
