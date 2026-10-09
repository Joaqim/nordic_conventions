---
title: "karrio advisor_nordic_conventions"
template: splash
hero:
  tagline: Non-blocking trade-document advisories for PostNord and DHL Freight Sweden shipments from Sweden, Denmark, and Finland, each citing the carrier or authority source it rests on.
  actions:
    - text: Advisory reference
      link: /karrio-advisor-nordic-conventions/concepts/advisories/
    - text: Development
      link: /karrio-advisor-nordic-conventions/development/
      variant: secondary
    - text: README on GitHub
      link: https://github.com/PrimePack-AB/karrio-advisor-nordic-conventions#readme
      variant: minimal
---

## What the plugin does

The plugin is an advisor-only extension for the karrio shipping SDK: it adds advisories to shipment responses, states what the consumer still owns, and never blocks or alters a shipment.
It declares shipment advisors only — no carrier mapper, proxy, settings, or address validator — and advises solely on shipments from Sweden, Denmark, or Finland to destinations outside the EU VAT area, plus the country-specific requirements DHL Freight Sweden names.
The advisories need a karrio SDK with the shipment advisors hook; see [Installation](guides/installation.md).
The README is the quick-start guide to installing, attesting, and reading the advisories; this site holds the reference pages behind it.

## Concepts

The concept pages explain when the plugin advises, how it reads territories, and every advisory it can return.

- [Scope](concepts/scope.md)
- [Territories](concepts/territories.md)
- [Advisory reference](concepts/advisories.md)

## Guides

The guides cover installing the plugin against the karrio fork and using attestations and the expected-procedures lookup.

- [Installation](guides/installation.md)
- [Attestations](guides/attestations.md)

## Development

The development pages are for working on the plugin itself: setup and tests, the package layout, and this documentation site.

- [Development](development/index.md)
- [Plugin layout](development/architecture/plugin-layout.md)
- [Documentation site](development/architecture/docs-site.md)
