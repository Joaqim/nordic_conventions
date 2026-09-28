import logging

import attr
import karrio.core.metadata as metadata

import karrio.plugins.nordic_conventions.rules.dhl_freight_sweden as dhl_freight_sweden
import karrio.plugins.nordic_conventions.rules.invoice_type as invoice_type
import karrio.plugins.nordic_conventions.rules.postnord as postnord
from karrio.plugins.nordic_conventions.procedures import Procedure, expected_procedures

ADVISORS = [
    postnord.se_no_digital_invoice,
    postnord.se_postpaket_commercial_invoice,
    postnord.se_export_paper_invoice,
    postnord.fi_export_invoice,
    postnord.dk_export_documents,
    dhl_freight_sweden.customs_mode_missing,
    dhl_freight_sweden.invoice_copy,
    dhl_freight_sweden.attached_documents,
    dhl_freight_sweden.voec_marking,
    invoice_type.invoice_type_content_mismatch,
]

# The stdlib logger is used because karrio.core.utils.logger is not
# guaranteed on karrio versions that predate the advisors hook.
HOOK_AVAILABLE = "shipment_advisors" in attr.fields_dict(metadata.PluginMetadata)

if not HOOK_AVAILABLE:
    logging.getLogger(__name__).warning(
        "karrio shipment advisors hook unavailable; nordic_conventions registers no advisors"
    )

METADATA = metadata.PluginMetadata(
    id="nordic_conventions",
    label="Nordic Conventions",
    description=(
        "Trade-document advisories for PostNord and DHL Freight Sweden shipments "
        "from Sweden, Denmark, and Finland to destinations outside the EU VAT area"
    ),
    status="beta",
    **(dict(shipment_advisors=ADVISORS) if HOOK_AVAILABLE else {}),
)
