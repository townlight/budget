## Windows 1.9.3.2 current release

Townlight for Windows 1.9.3.2 is the current signed public beta. See the [release notes](https://github.com/townlight/townlight/releases/tag/townlight-windows-v1.9.3.2) and [acceptance record](https://github.com/townlight/townlight/releases/download/townlight-windows-v1.9.3.2/ACCEPTANCE-Windows-1.9.3.2.md).

Townlight Windows 1.9.3.2 is a signed Suite package; Data, Budget, and Grants were first bundled in Windows 1.9.3.1 and remain in the current signed 1.9.3.2 Windows beta.

# Townlight Budget

Townlight Budget Windows package, package `townlight-budget` `0.2.0`. Packaged with Windows beta 1.9.3.2; not a standalone software release. See the [GitHub release](https://github.com/townlight/townlight/releases/tag/townlight-windows-v1.9.3.2).

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
