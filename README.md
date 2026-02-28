# ha-voicemeeter

A Home Assistant custom integration that exposes [Voicemeeter](https://vb-audio.com/Voicemeeter/) as controllable entities in HA. A separate Windows [companion app](https://github.com/Skrubbadubba/voicemeeter-ha-windows-companion) bridges the Voicemeeter DLL to the network via WebSocket. This integration will not connect to anything unless you got the companion app!



## Requirements

This integration was developed and tested on HA core 2025.2.4, it may or may not work on earlier versions.

- Voicemeeter Basic, Banana, or Potato installed on a Windows PC
- The ha-voicemeeter companion app running on that same Windows PC

## Installation

### Companion App (Windows)

Download the latest release from the [releases page](https://github.com/Skrubbadubba/voicemeeter-ha-windows-companion/releases) and run `voicemeeter-companion.exe`. It will start a WebSocket server on port 27001. Voicemeeter must be running before you start the companion app.

To run it automatically on startup:

1. Right click, the exe and create a shortcut.
2. Hit <kbd>WIN</kbd> + <kbd>r</kbd> and enter `shell:startup`.
3. Add the shortcut to the folder

### Integration (Home Assistant)

1. Copy the `custom_components/voicemeeter` folder into your HA `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings → Integrations → Add Integration** and search for **Voicemeeter**.
4. ***(Optional):*** Enter a name
5. Enter the IP address of your Windows PC and the port (default: 27001). Note the port on the companion app cannot be changed, so do not change the default.

## Entities

All entities are grouped under a single device per config entry.

Multiple entries are not tested, but probably works.

### Mute switches
One per strip and bus. These appear in the main entity list and are suitable for automations.

### Gain sliders
One per strip and bus, ranging from -60 dB to +12 dB. These are `EntityCategory.CONFIG` — they show up under the device but are kept out of the main dashboard.

### Routing switches
One per strip per bus output (e.g. 25 switches on Banana). These control whether a strip is routed to a given bus (A1, A2, B1, etc). Also `EntityCategory.CONFIG`.

### Entity counts by variant

| Variant | Strips | Buses | Mute switches | Gain sliders | Routing switches |
| ------- | ------ | ----- | ------------- | ------------ | ---------------- |
| Basic   | 3      | 2     | 5             | 5            | 6                |
| Banana  | 5      | 5     | 10            | 10           | 25               |
| Potato  | 8      | 8     | 16            | 16           | 40               |


## Naming

Strip names come from Voicemeeter itself (user-defined labels). If a strip has no label set, the integration falls back to canonical names:

- **Basic:** Stereo Input 1–2, Voicemeeter Input
- **Banana:** Stereo Input 1–3, Voicemeeter Input, Voicemeeter AUX Input
- **Potato:** Stereo Input 1–5, Voicemeeter Input, Voicemeeter AUX Input, Voicemeeter VAIO3

Bus names work the same. If a bus has no label, the canonical names will be used:

- **Basic:** A, B
- **Banana:** A1-A3, B1-B2
- **Potato:** A1-A5, B1–B3

## Planned features

### Soon hopefully

- [ ] Select entities for device selection for hardware strips and buses
- [ ] Button entities for macro buttons

### Maybe

- [ ] VBAN controls
- [ ] A separate VBAN media player integration

