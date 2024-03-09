import base64

from datetime import datetime
import re

import uuid

from bs4 import BeautifulSoup
import requests


class AstroAssistant:
    URL_PATTERN = "http://clearoutside.com/forecast/%s/%s"

    def __init__(self, lat, lng):
        self.__lat = lat
        self.__lng = lng

    def fetch_forecast(self):
        response = requests.get(self.get_url())
        return response.text

    def get_url(self):
        return AstroAssistant.URL_PATTERN % (self.__lat, self.__lng)

    def get_forecast(self):
        data = self.fetch_forecast()
        self.soup = BeautifulSoup(data, "html.parser")

        forecast = []
        days_data = []
        for day in range(0, 8):
            days_data += self.soup.find_all("div", id="day_%i" % day)

        for day_idx, day_data in enumerate(days_data):
            day = day_data.find_next('div', class_="fc_day_date").find_all('span')[0].get_text()
            date = day_data.find_next('div', class_="fc_day_date").get_text().split()[1]
            times = day_data.find_all_next("div", class_="fc_daylight")[0].text
            m = re.match('.+Civil Dark: ([0-9:]+) - ([0-9:]+)\..+', times)
            begin = m.group(1)
            end = m.group(2)

            element = day_data.find_all_next("div", class_="fc_hour_ratings")[0].find_all_next("ul")[0]
            elements = element.find_all_next("li")[0:24]

            hourly = {}
            idx = 23
            min_hour = min(int(begin.split(':')[0]), int(end.split(':')[0]) - 1)
            max_hour = max(int(begin.split(':')[0]), int(end.split(':')[0]) - 1)
            for li in elements:
                expected_condition = li['class'][0].split('_')[1]
                if expected_condition in ['ok', 'good'] and idx in range(min_hour, max_hour):
                    hourly[idx] = expected_condition

                if idx == 23:
                    idx = 0
                else:
                    idx += 1

            if hourly.__len__() > 0:
                forecast.append("%s %s at %s hour" % (day, date, idx))

        return forecast

    def update_forecast_feed(self):
        forecast = self.get_forecast()

        link = self.get_url()
        _id = uuid.uuid4()
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        msg = None

        if forecast.__len__() > 0:
            msg = "Good conditions forecasted on "
            msg += ", ".join(forecast)
        else:
            msg = 'No good seeing forecasted in the next 7 days.'

        entry = []

        entry.append(f"<entry>\n")
        entry.append(f"<title>{timestamp} astronomical forcast</title>\n")
        entry.append(f"<link href=\"{link}\"/>\n")
        entry.append(f"<id>urn:uuid:{_id}</id>\n")
        entry.append(f"<updated>{timestamp}</updated>\n")
        entry.append(f"<summary>{msg}</summary>\n")
        entry.append(f"</entry>\n")
        entry.append(f"<updated>{timestamp}</updated>\n")
        entry.append("</feed>\n")

        with open('./klastro.atom', 'r+') as f:
            data = f.readlines()
            data.pop()
            data.pop()
            data.extend(entry)

        with open('./klastro.atom', 'r+') as f:
            f.writelines(data)


def entry_point(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    if "data" in event:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        print(pubsub_message)

    lat = "45.98"
    lng = "6.16"

    co = AstroAssistant(lat, lng)
    co.update_forecast_feed()


if __name__ == "__main__":
    entry_point({}, None)
