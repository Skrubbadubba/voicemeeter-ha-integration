import logging

DOMAIN = "voicemeeter"
LOGGER = logging.getLogger(__package__)

CONF_HOST = "host"
CONF_PORT = "port"
CONF_KIND = "kind"
CONF_NAME = "name"

DEFAULT_PORT = 27001
DEFAULT_KIND = "banana"

VOICEMEETER_KINDS = ["basic", "banana", "potato"]

KIND_HARDWARE_STRIPS = {"basic": 2, "banana": 3, "potato": 5}
KIND_VIRTUAL_STRIPS = {"basic": 1, "banana": 2, "potato": 3}
KIND_BUSES = {"basic": 2, "banana": 5, "potato": 8}

BUS_LABELS = {
    "basic": ["A1", "A2", "B1"],
    "banana": ["A1", "A2", "A3", "B1", "B2"],
    "potato": ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3"],
}


def get_bus_label(kind: str, index: int) -> str:
    labels = BUS_LABELS.get(kind, [])
    if index < len(labels):
        return labels[index]
    return f"Bus {index}"


STRIP_LABELS = {
    "basic": ["Stereo Input 1", "Stereo Input 2", "Voicemeeter Input"],
    "banana": [
        "Stereo Input 1",
        "Stereo Input 2",
        "Stereo Input 3",
        "Voicemeeter Input",
        "Voicemeeter AUX Input",
    ],
    "potato": [
        "Stereo Input 1",
        "Stereo Input 2",
        "Stereo Input 3",
        "Stereo Input 4",
        "Stereo Input 5",
        "Voicemeeter Input",
        "Voicemeeter AUX Input",
        "Voicemeeter VAIO3",
    ],
}


def get_strip_label(kind: str, index: int) -> str:
    labels = STRIP_LABELS.get(kind, [])
    if index < len(labels):
        return labels[index]
    return f"Strip {index}"
