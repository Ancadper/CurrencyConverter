# Currency converter for NVDA

Currency converter is an NVDA add-on that converts amounts between currencies using the public Frankfurter API.

## Features

- Accessible window from NVDA's Tools menu.
- Currency conversion using Frankfurter API.
- Currency list loaded from the API and sorted alphabetically.
- Recent conversions history during the current NVDA session only.
- Configurable input gestures with no default shortcuts assigned.
- Quick conversion from an input gesture, asking for the amount and copying the result to the clipboard.
- English interface by default, with Spanish translation included.

## Privacy

When you convert an amount, the add-on sends the amount, source currency and target currency to Frankfurter API. It does not send personal information or the conversion history.

The add-on stores locally only the last amount and the last selected currencies. The recent conversions history is temporary and is cleared when NVDA is closed or restarted.

## Requirements

- NVDA 2023.1 or later.
- Internet connection for live exchange rates.

## License

GPL-2.0-or-later.

## Author

Arash <arash@ancadper.com>
