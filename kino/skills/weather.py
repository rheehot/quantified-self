# -*- coding: utf-8 -*-

import arrow
import forecastio
from geopy.geocoders import Nominatim
from hbconfig import Config
from urllib import parse

from ..open_api.airkoreaPy import AirKorea

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter
from ..slack.template import MsgTemplate

from ..utils.data_handler import DataHandler
from ..utils.logger import Logger
from ..utils.profile import Profile


class Weather(object):
    def __init__(self, slackbot=None):
        self.logger = Logger().get_logger()
        self.data_handler = DataHandler()
        self.profile = Profile()

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def forecast(self, timely="current"):
        cache_data = self.data_handler.read_cache()

        user_location = self.profile.get_location()
        parsed_user_location = parse.quote(user_location)  # user_location is Korean

        if parsed_user_location in cache_data:
            address = cache_data[parsed_user_location]["address"]
            lat = cache_data[parsed_user_location]["lat"]
            lon = cache_data[parsed_user_location]["lon"]
        else:
            geolocator = Nominatim(user_agent="kino-bot")
            location = geolocator.geocode(user_location)

            address = location.address
            lat = location.latitude
            lon = location.longitude

            self.data_handler.edit_cache(
                (parsed_user_location, {"address": address, "lat": lat, "lon": lon})
            )

        api_key = Config.open_api.dark_sky.TOKEN
        dark_sky = forecastio.load_forecast(api_key, lat, lon)

        if timely == "current":
            currently = dark_sky.currently()
            self.__forecast(currently, timely, address)
        elif timely == "daily":
            hourly = dark_sky.hourly()
            self.__forecast(hourly, timely, address)
        elif timely == "weekly":
            daily = dark_sky.daily()
            self.__forecast(daily, timely, address)

    def __forecast(self, forecast, timely, address):
        icon = forecast.icon
        summary = forecast.summary

        if timely == "current":
            temperature = str(forecast.temperature) + "도"
            fallback = summary + " " + temperature
        else:
            temperature = self.__hourly_temperature(forecast)
            fallback = summary + " " + temperature

        attachments = MsgTemplate.make_weather_template(
            address, icon, summary, temperature=temperature, fallback=fallback
        )
        self.slackbot.send_message(attachments=attachments)

    def __hourly_temperature(self, forecast):
        hourly_temp = []
        h = forecast.data
        for i in range(0, 24, 3):
            time = arrow.get(h[i].d["time"], tzinfo=self.profile.get_timezone()).format(
                "D일 H시"
            )
            temperature = h[i].d["temperature"]
            hourly_temp.append("- " + time + ": " + str(temperature) + "도")
        hourly_temp = "\n".join(hourly_temp)
        return hourly_temp

    def air_quality(self):
        api_key = Config.open_api.airkorea.TOKEN
        airkorea = AirKorea(api_key)

        station_name = self.profile.get_location(station=True)

        try:
            response = airkorea.forecast(station_name)
            attachments = MsgTemplate.make_air_quality_template(station_name, response)
            self.slackbot.send_message(attachments=attachments)
        except BaseException:
            self.logger.exception("air_auality")
            self.slackbot.send_message(text=MsgResource.ERROR)
