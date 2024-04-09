def _get_api():
    import pytolnet
    api = pytolnet.TOLNetAPI()
    return api


def test_calendar():
    api = _get_api()
    cldf = api.data_calendar('UAH')
    assert 2115 in cldf.index.values
    try:
        api.data_calendar('notreal')
    except KeyError:
        pass


def test_producttype4():
    import tempfile

    api = _get_api()
    newest_data_id = 2115
    with tempfile.TemporaryDirectory() as td:
        ds = api.to_xarray(newest_data_id, overwrite=True, cache=td)
        sumdf = ds.to_dataframe().reset_index().describe()
        assert 'time' in sumdf.columns
        assert 'altitude' in sumdf.columns
        assert 'derived_ozone' in sumdf.columns
        assert ds.sizes['time'] > 0
        assert ds.sizes['altitude'] > 0


def test_producttype5():
    import tempfile

    api = _get_api()
    newest_data_id = 4658
    with tempfile.TemporaryDirectory() as td:
        ds = api.to_xarray(newest_data_id, overwrite=True, cache=td)
        sumdf = ds.to_dataframe().reset_index().describe()
        assert 'time' in sumdf.columns
        assert 'altitude' in sumdf.columns
        assert 'derived_ozone' in sumdf.columns
        assert ds.sizes['time'] > 0
        assert ds.sizes['altitude'] > 0


def test_producttype8():
    import tempfile

    api = _get_api()
    newest_data_id = 4658
    with tempfile.TemporaryDirectory() as td:
        try:
            api.to_xarray(newest_data_id, product_type=8, cache=td)
        except IOError:
            pass
