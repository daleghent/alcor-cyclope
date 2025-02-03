import sys
import json
import traceback
from datetime import datetime, timezone
from alcor_cyclope.client import AlcorCyclopeClient

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [-j] <server_host>")
        sys.exit(1)

    json_output = False
    args = sys.argv[1:]

    if "-j" in args:
        json_output = True
        args.remove("-j")

    if not args:
        print(f"Usage: {sys.argv[0]} [-j] <server_host>")
        sys.exit(1)

    host = args[0]
    client = AlcorCyclopeClient(host)

    try:
        client.connect()

        status_code = client.get_status()
        status_string = client.translate_status(status_code)
        data = client.get_data() or {}

        if json_output:
            data['measurement_date_utc'] = data['measurement_date_utc'].isoformat()
            data['measurement_date_local'] = data['measurement_date_local'].isoformat()
            data['status_code'] = status_code
            data['status'] = status_string

            print(json.dumps(data, indent=4))
            return

        valid = data.get("valid", False)
        meas_date_utc = data.get("measurement_date_utc", None)
        meas_date_local = data.get("measurement_date_local", "N/A")
        zenith_arcsec = data.get("last_zenith_arcsec", "N/A")
        r0_arcsec = data.get("last_r0_arcsec", "N/A")

        if valid and meas_date_utc:
            now = datetime.utcnow().replace(tzinfo=timezone.utc)
            timediff = (now - meas_date_utc).total_seconds()

            print(f"Status: {status_string}")
            print(f"Last Measurement: {timediff:.2f} seconds ago at "
                  f"{meas_date_utc.strftime('%x %X %Z')} "
                  f"({meas_date_local} local)")
            print(f"Last Zenith Arcsec: "
                  f"{zenith_arcsec if zenith_arcsec is not None else 'Invalid value'}")
            print(f"Last R0 Arcsec: {r0_arcsec if r0_arcsec is not None else 'Invalid value'}")
        else:
            print(f"Invalid reading. Status: {status_string}")
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.stderr.write(traceback.format_exc())
    finally:
        client.close()

if __name__ == "__main__":
    main()
