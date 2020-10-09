import hug
from nea_weather import NeaWeatherProcessing, download_rain_file

@hug.get()
def rain(long: float, lat: float, buffer=0.009):
    file = download_rain_file(mode="memory")
    nea = NeaWeatherProcessing(file)
    return nea.check_rain(long, lat, buffer)