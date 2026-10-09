import typing

import karrio.lib as lib
import karrio.core.models as models
import karrio.core.advisors as advisors

ADDRESSES = dict(
    SE=dict(country_code="SE", postal_code="11122", city="Stockholm"),
    SE_TAXED=dict(country_code="SE", postal_code="11122", city="Stockholm", federal_tax_id="SE556677889901"),
    SE_STATE_TAXED=dict(country_code="SE", postal_code="11122", city="Stockholm", state_tax_id="SE202401987654"),
    NO=dict(country_code="NO", postal_code="0150", city="Oslo"),
    DK=dict(country_code="DK", postal_code="2100", city="København"),
    FI=dict(country_code="FI", postal_code="00100", city="Helsinki"),
    AX=dict(country_code="FI", postal_code="22100", city="Mariehamn"),
    AX_CODE=dict(country_code="AX", postal_code="22100", city="Mariehamn"),
    AX_PREFIXED=dict(country_code="AX", postal_code="AX-22100", city="Mariehamn"),
    DE=dict(country_code="DE", postal_code="10115", city="Berlin"),
    GR=dict(country_code="GR", postal_code="10431", city="Athens"),
    GR_TAXED=dict(country_code="GR", postal_code="10431", city="Athens", federal_tax_id="EL998877665"),
    CY=dict(country_code="CY", postal_code="1010", city="Nicosia"),
    CY_BUSINESS=dict(
        country_code="CY", postal_code="1010", city="Nicosia", company_name="Ledra Trading Ltd"
    ),
    CY_RESIDENTIAL=dict(
        country_code="CY",
        postal_code="1010",
        city="Nicosia",
        company_name="Ledra Trading Ltd",
        residential=True,
    ),
    PL=dict(country_code="PL", postal_code="00-001", city="Warsaw"),
    RO=dict(country_code="RO", postal_code="010011", city="Bucharest"),
    ES=dict(country_code="ES", postal_code="28001", city="Madrid"),
    HU=dict(country_code="HU", postal_code="1011", city="Budapest"),
    IC=dict(country_code="ES", postal_code="35 001", city="Las Palmas"),
    CH=dict(country_code="CH", postal_code="8001", city="Zürich"),
    GB=dict(country_code="GB", postal_code="SW1A 1AA", city="London"),
    JE=dict(country_code="JE", postal_code="JE2 3AB", city="St Helier"),
    GB_JE=dict(country_code="GB", postal_code="JE2 3AB", city="St Helier"),
    IM=dict(country_code="IM", postal_code="IM1 1AA", city="Douglas"),
    IC_CODE=dict(country_code="IC", postal_code="35001", city="Las Palmas"),
    AX_MAINLAND=dict(country_code="AX", postal_code="00100", city="Helsinki"),
    AX_NO_POSTAL_CODE=dict(country_code="AX", city="Mariehamn"),
    IC_MAINLAND=dict(country_code="IC", postal_code="28001", city="Madrid"),
    FO=dict(country_code="FO", postal_code="FO-100", city="Tórshavn"),
    GL_FAROESE=dict(country_code="GL", postal_code="100", city="Tórshavn"),
    XI=dict(country_code="XI", postal_code="BT1 1AA", city="Belfast"),
    XI_NON_BT=dict(country_code="XI", postal_code="EC1A 1BB", city="London"),
    LI=dict(country_code="LI", postal_code="9490", city="Vaduz"),
    US=dict(country_code="US", postal_code="10001", city="New York"),
    UA=dict(country_code="UA", postal_code="01001", city="Kyiv"),
    IS=dict(country_code="IS", postal_code="101", city="Reykjavík"),
)

PARCELS = [dict(weight=1.0, weight_unit="KG")]

COMMODITIES = [
    dict(
        description="T-shirt",
        quantity=1,
        weight=0.2,
        weight_unit="KG",
        value_amount=200.0,
        value_currency="SEK",
        origin_country="SE",
    )
]


def customs(
    content_type: typing.Optional[str] = None,
    commercial_invoice: typing.Optional[bool] = None,
    **options,
) -> dict:
    return lib.to_dict(
        dict(
            commodities=COMMODITIES,
            content_type=content_type,
            commercial_invoice=commercial_invoice,
            options=options or None,
        )
    )


def shipment(
    shipper: str,
    recipient: str,
    service: str,
    customs: typing.Optional[dict] = None,
    options: typing.Optional[dict] = None,
    parcels: typing.Optional[typing.List[dict]] = None,
    is_return: bool = False,
) -> models.ShipmentRequest:
    return lib.to_object(
        models.ShipmentRequest,
        lib.to_dict(
            dict(
                service=service,
                shipper=ADDRESSES[shipper],
                recipient=ADDRESSES[recipient],
                parcels=parcels or PARCELS,
                customs=customs,
                options=options,
                is_return=is_return or None,
            )
        ),
    )


def context(
    carrier_name: str, operation: str = "shipping"
) -> advisors.AdvisorContext:
    return advisors.AdvisorContext(
        carrier_name=carrier_name,
        carrier_id=f"{carrier_name}_test",
        operation=operation,
    )


def messages(advisor, request, context) -> typing.List[dict]:
    return lib.to_dict(list(advisor(request, context)))
