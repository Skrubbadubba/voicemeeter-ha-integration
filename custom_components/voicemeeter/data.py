from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .coordinator import VoicemeeterCoordinator
    from .websocket import VoicemeeterWebSocket


# ---------------------------------------------------------------------------
# State models
# ---------------------------------------------------------------------------


@dataclass
class StripData:
    index: int
    label: str
    mute: bool
    gain: float
    virtual: bool
    a1: bool
    a2: bool
    a3: bool
    a4: bool
    a5: bool
    b1: bool
    b2: bool
    b3: bool


@dataclass
class BusData:
    index: int
    label: str
    mute: bool
    gain: float


@dataclass
class VoicemeeterState:
    kind: str
    protocol: str
    strips: list[StripData] = field(default_factory=list)
    buses: list[BusData] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Runtime data (stored in entry.runtime_data)
# ---------------------------------------------------------------------------


@dataclass
class VoicemeeterRuntimeData:
    coordinator: VoicemeeterCoordinator
    ws: VoicemeeterWebSocket


# ---------------------------------------------------------------------------
# Message parsing
# ---------------------------------------------------------------------------


def parse_state_message(msg: dict[str, Any]) -> VoicemeeterState:
    """
    Parse a full state dump from the companion app.

    Expected message shape:
    {
        "type": "state",
        "kind": "banana",
        "strips": [{"index": 0, "label": "Mic", "mute": false, "gain": 0.0, "virtual": false}, ...],
        "buses":  [{"index": 0, "label": "A1",  "mute": false, "gain": 0.0}, ...]
    }
    """
    strips = [
        StripData(
            index=s["index"],
            label=s.get("label", f"Strip {s['index']}"),
            mute=s["mute"],
            gain=s["gain"],
            virtual=s["virtual"],
            a1=s["a1"],
            a2=s["a2"],
            a3=s["a3"],
            a4=s["a4"],
            a5=s["a5"],
            b1=s["b1"],
            b2=s["b2"],
            b3=s["b3"],
        )
        for s in msg.get("strips", [])
    ]

    buses = [
        BusData(
            index=b["index"],
            label=b.get("label", f"Bus {b['index']}"),
            mute=b["mute"],
            gain=b["gain"],
        )
        for b in msg.get("buses", [])
    ]

    return VoicemeeterState(kind=msg["kind"], protocol=msg["protocol"], strips=strips, buses=buses)


def apply_update_message(
    state: VoicemeeterState, msg: dict[str, Any]
) -> VoicemeeterState:
    """
    Apply a single-parameter update to a copy of the current state.

    Expected message shape:
    {"type": "update", "target": "strip", "index": 0, "param": "mute", "value": true}

    Returns a new VoicemeeterState rather than mutating the existing one.
    This keeps coordinator.data immutable between updates, which avoids
    any risk of partial state being read by an entity mid-update.
    """
    target = msg["target"]  # "strip" or "bus"
    index = msg["index"]
    param = msg["param"]  # "mute" or "gain" or bus labels
    value = msg["value"]

    new_strips = list(state.strips)
    new_buses = list(state.buses)

    if target == "strip":
        new_strips = [
            _apply_to_strip(s, param, value) if s.index == index else s
            for s in new_strips
        ]
    elif target == "bus":
        new_buses = [
            _apply_to_bus(b, param, value) if b.index == index else b for b in new_buses
        ]

    return VoicemeeterState(kind=state.kind, protocol=state.protocol, strips=new_strips, buses=new_buses)


def _apply_to_strip(strip: StripData, param: str, value: Any) -> StripData:
    return StripData(
        index=strip.index,
        label=strip.label,
        mute=value if param == "mute" else strip.mute,
        gain=value if param == "gain" else strip.gain,
        virtual=strip.virtual,
        a1=value if param == "a1" else strip.a1,
        a2=value if param == "a2" else strip.a2,
        a3=value if param == "a3" else strip.a3,
        a4=value if param == "a4" else strip.a4,
        a5=value if param == "a5" else strip.a5,
        b1=value if param == "b1" else strip.b1,
        b2=value if param == "b2" else strip.b2,
        b3=value if param == "b3" else strip.b3,
    )


def _apply_to_bus(bus: BusData, param: str, value: Any) -> BusData:
    return BusData(
        index=bus.index,
        label=bus.label,
        mute=value if param == "mute" else bus.mute,
        gain=value if param == "gain" else bus.gain,
    )
