# Release-calendar, freshness and failure hardening

## Official timeliness

The ECB CISS data-information page states that New CISS is calculated daily and is updated daily with the data of the previous day, except for China. The production series in this repository is the Euro-area New CISS.

The first successful GitHub-hosted full-history acquisition contained every Monday-Friday calendar date from 1980-01-03 through 2026-10-20. This includes dates that are common euro-area public holidays, so the operational observation calendar does not apply a separate holiday-exclusion list.

For the proposed 17:23 UTC production acquisition, the expected latest observation is therefore the latest Monday-Friday date strictly before the UTC acquisition date.

## Freshness

The release audit counts missing expected observation dates between the last official observation and the expected latest date:

- 0-2 missing expected dates: HEALTHY
- 3-5: DEGRADED
- more than 5: FAILED

Trusted current publication requires HEALTHY. Any historical Monday-Friday gap causes fail-closed validation.

## Failure injection

Automated tests now exercise at least:

- wrong series identity;
- duplicate observation date;
- full/tail release race;
- historical weekday gap;
- degraded and failed freshness boundaries;
- current previous-day release success.

These are technical validation states, not new Silver signal-model states.
