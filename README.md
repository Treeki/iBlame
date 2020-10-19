This slapdash pair of Python 3 scripts deals with a problem I ran into with
iCloud Family Sharing.

All purchases made by users who are part of an iCloud Family go through the
payment method associated with the family owner - the only way to bypass this
is for individual users to top up their own account with iTunes credit,
externally. This means that every time one of my friends buys an app or
subscribes to Grindr Xtra, it comes off my credit card.

Thankfully, Apple sends me an email every time a transaction happens, and it's
fairly easy to parse these.

I set up a Fastmail filter which moves emails from `no_reply@email.apple.com`
with the subject `Your invoice from Apple.` into a specific folder.

The `imap-download.py` script in this repository connects to Fastmail and
fetches all the emails in this folder, storing them into individual files in
the `emails/` directory.

Then, `email-parser.py` scans every email in the directory and extracts the
information, building a simple table of:

- transaction dates
- the amount that came from the user's iTunes store credit
- the amount that came off my credit card
- the name associated with the Apple ID
- the items contained within that transaction

```
2018-07-19 |  699 |    0 | ninji | iCloud: 2 TB Storage Plan
2018-07-22 | 1399 |    0 | ninji | Affinity Designer
2018-09-02 |    0 |  499 | ninji | Donut County
2018-09-02 |  309 |  390 | ninji | iCloud: 2 TB Storage Plan
```

It also builds a running total of how much each Apple ID has charged to my
card, and displays this at the end.

This could probably do more intelligent things (like maybe automatically
notifying the user in question), but I'm happy with this for now as it still
gives me a way to figure out how much people owe me without manually going
through tons of invoice emails.

### config.json

This file defines stuff that's used by both of the Python scripts, both to
download the emails using IMAP and to parse them.

The `imap_` keys are fairly self-explanatory.

`billed_to_combo` is the "BILLED TO" text in the invoice used for payments
that use a mix of store credit and a regular card transaction (e.g. when your
iTunes balance isn't enough to cover the whole payment).

`billed_to_prefix` is the text that the "BILLED TO" entry starts with for card
payments - it uses a prefix because it ends with the last 4 digits of the card
number.

`total_keywords` is the text that identifies the line containing the card
transaction's total, for mixed payments.

`currency` is the prefix for prices, which gets stripped.
