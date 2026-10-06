"""Advisory codes of the Nordic conventions plugin.

Every advisory code value is the plugin identity advisor_nordic_conventions_, matching
PLUGIN_ID, the package name, and the karrio.plugins entry-point name, followed
by scope and topic segments, all lower_snake_case.
Codes are consumer-facing API surface, so renaming one is a breaking change.
"""

import enum


class AdvisoryClassification(str, enum.Enum):
    postnord_se_no_digital_invoice = "advisor_nordic_conventions_postnord_se_no_digital_invoice"
    postnord_se_postpaket_commercial_invoice = "advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice"
    postnord_se_export_paper_invoice = "advisor_nordic_conventions_postnord_se_export_paper_invoice"
    postnord_fi_export_invoice = "advisor_nordic_conventions_postnord_fi_export_invoice"
    postnord_dk_export_documents = "advisor_nordic_conventions_postnord_dk_export_documents"
    dhl_freight_sweden_customs_mode_missing = "advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing"
    dhl_freight_sweden_invoice_copy = "advisor_nordic_conventions_dhl_freight_sweden_invoice_copy"
    dhl_freight_sweden_attached_documents = "advisor_nordic_conventions_dhl_freight_sweden_attached_documents"
    dhl_freight_sweden_voec_marking = "advisor_nordic_conventions_dhl_freight_sweden_voec_marking"
    invoice_type_content_mismatch = "advisor_nordic_conventions_invoice_type_content_mismatch"
    attestation_conflict = "advisor_nordic_conventions_attestation_conflict"
    ch_discount_on_invoice = "advisor_nordic_conventions_ch_discount_on_invoice"
    zero_value_line = "advisor_nordic_conventions_zero_value_line"
    dhl_freight_sweden_parcel_connect_not_served = "advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served"
    dhl_freight_sweden_parcel_connect_gb_agreement = "advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement"
