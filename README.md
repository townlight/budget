# Townlight Budget

Townlight Budget Windows candidate, package `townlight-budget` `0.2.0`. Source candidate only; not a software release.

Depends on exact `townlight-core==1.3.0.dev2`.

## Scope

Uses existing roles and records:

- Windows full profile
- CSV draft and original workpapers
- City-staff/admin review
- Saved public Meetings packet and clerk/admin adoption record
- Local-admin queue approval and resident export via Data to configured Portal

Accounting, payroll, and ERP remain external.

## Workpaper API

Standalone namespace `townlight_budget.main:app` for workpaper API only. Existing endpoint paths are preserved.

## Documentation

- [User manual](USER-MANUAL.md)
- [Documentation index](docs/index.html)
