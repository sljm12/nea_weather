from nea_weather import NeaWeatherProcessing

rain_file = "./dpsri_70km_2020100807100000dBR.dpsri.png"
no_rain_file = "./dpsri_70km_2020100812400000dBR.dpsri.png"
test_location = (103.8752, 1.3715)


def test_is_raining():
    nea = NeaWeatherProcessing(rain_file)
    assert nea.check_rain(test_location[0], test_location[1], 0.009) is True


def test_is_raining_full():
    nea = NeaWeatherProcessing(rain_file)
    data = nea.get_is_raining_full(test_location[0], test_location[1],  0.009)
    assert len(data) == 2
