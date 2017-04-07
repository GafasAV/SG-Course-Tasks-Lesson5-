import requests
import argparse
import logging
import sys


__author__ = "Andrew Gafiychuk"


API_KEY = "4e8485185c9fdf9d9b73dd9a8e1aaefb"
URL = "http://api.openweathermap.org/data/2.5/weather"


def weather_request(params):
    """
    This function takes params like ID or Location
    do request to server, GET data, parse it and print.
    
    If rise ERROR, function print ERR-CODE and print message.
    
    """
    response = requests.get(url=URL, params=params)

    if response.status_code == 200:
        data = response.json()

        print("Current temp: {0:.2f}\xb0 C"
              .format(data["main"]["temp"] % 273.15))
        print("City: {0} (country: {1})"
              .format(data["name"], data["sys"]["country"]))

    else:
        data = response.json()
        print("Some error: {0} [{1}]"
              .format(response.status_code, data["message"]))


def create_parser():
    """
    Function create and return params list for parsing.
    
    """
    logging.debug("[-]Parser created...")

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "-I", "--id", type=int)
    parser.add_argument("-l", "-L", "--location", type=str)

    return parser


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.debug("[-]Application started...")

    if len(sys.argv) <= 1:
        print("No parameters specified ...")
        print("Usage: <-command> [value] \n")
        print("  Use -l to specify city name (-l Kiev) "
              "or (--location Kiev)")
        print("  Use -i to specify city id (-i 703448) "
              "or (--id 703448)")

        logging.debug("[-]No params -EXITING...")
        sys.exit(1)
    else:
        logging.debug("[-]Begin parse params...")

        parser = create_parser()
        params = parser.parse_args(sys.argv[1:])

        if params.location and params.id:
            logging.debug("[-]GET data by id...(Two params Specified !)")

            params_by_id = {"id": params.id, "appid": API_KEY}
            weather_request(params_by_id)
        elif params.id:
            logging.debug("[-]GET data by id...")

            params_by_id = {"id": params.id, "appid": API_KEY}
            weather_request(params_by_id)
        elif params.location:
            logging.debug("[-]GET data by location...")

            params_by_location = {"q": params.location,
                                  "appid": API_KEY}
            weather_request(params_by_location)

        logging.debug("[-]Data printing -EXITING...")
        sys.exit(0)