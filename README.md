# Alcor Cyclope Seeing Monitor TCP API Client

A simple client to interact with the TCP API service of the Cyclope seeing monitor control app.

## Installation

```
pip install alcor_cyclope
```

## Command-line interface usage
```
cyclope [-j] <server_ip>
```

## Example CLI output
```
# cyclope 192.168.1.20
Status: Measuring
Last Measurement: 2.34 seconds ago at 02/03/25 06:01:10 UTC (Sun Feb  2 23:01:10 2025 local)
Last Zenith Arcsec: 1.37
Last R0 Arcsec: 83.09
```

With JSON output:

```
# cyclope -j 192.168.1.20
{
    "valid": true,
    "measurement_jd_utc": 45691.5601288,
    "measurement_date_utc": "2025-02-03T13:26:35+00:00",
    "measurement_jd_local": 45691.2684621,
    "measurement_date_local": "2025-02-03T06:26:35",
    "last_zenith_arcsec": 1.06,
    "last_r0_arcsec": 106.57,
    "status_code": 2,
    "status": "Idle (Daytime)"
}
```
