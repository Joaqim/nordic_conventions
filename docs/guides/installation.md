---
title: "Installation"
---

Install the plugin from GitHub:

```bash
pip install "git+https://github.com/PrimePack-AB/karrio-advisor-nordic-conventions.git"
```

The plugin registers through the `karrio.plugins` entry point group under the id `advisor_nordic_conventions` and is reported with the plugin type `advisor`.
Installing it adds messages to shipment responses; uninstalling it removes them.

## The karrio fork requirement

The advisories need a karrio SDK with the shipment advisors hook, which only the [karrio fork](https://github.com/Joaqim/karrio) branch `feat-shipment-advisors` provides.
With released karrio the plugin installs and loads but registers no advisors, so it changes nothing; it logs once that the hook is unavailable and leaves shipment responses unchanged.
Until the feature merges and ships in a karrio release, a working setup requires a local checkout of the fork; see [Development](../development/index.md#setup).
