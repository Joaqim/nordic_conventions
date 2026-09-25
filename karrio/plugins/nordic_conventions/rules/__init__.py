"""Advisory rules of the Nordic conventions plugin."""

import typing

import karrio.core.models as models

import karrio.plugins.nordic_conventions.lanes as lanes
import karrio.plugins.nordic_conventions.sources as sources

PLUGIN_ID = "nordic_conventions"


def advisory(
    code: str,
    level: str,
    text: str,
    lane: lanes.Lane,
    cited: typing.Sequence[sources.Source],
    **details,
) -> models.Message:
    """One advisory message citing its sources; the SDK fills the carrier identity."""
    return models.Message(
        carrier_name=None,
        carrier_id=None,
        code=code,
        level=level,
        message=text,
        details=dict(
            plugin=PLUGIN_ID,
            lane=f"{lane.shipper_country}-{lane.recipient_country}",
            sources=[source.to_dict() for source in cited],
            **details,
        ),
    )
