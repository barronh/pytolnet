def _get_api():
    from .. import TOLNetAPI
    api = TOLNetAPI()
    return api


def test_product_types():
    api = _get_api()
    ptdf = api.product_types()
    assert 'product_type_name' in ptdf.columns
    assert 'description' in ptdf.columns


def test_file_types():
    api = _get_api()
    ftdf = api.file_types()
    assert 'file_type_name' in ftdf.columns
    assert 'description' in ftdf.columns


def test_calendar():
    api = _get_api()
    cldf = api.data_calendar('UAH')
    assert cldf.shape[0] > 0
    try:
        api.data_calendar('notreal')
        raise TypeError()
    except KeyError:
        pass


def _test_product(igname, product_type):
    import tempfile

    api = _get_api()
    cldf = api.data_calendar(igname, product_type=product_type)
    newest_data_id = cldf.index.values.max()
    with tempfile.TemporaryDirectory() as td:
        ds = api.to_dataset(newest_data_id, overwrite=True, cache=td)
        sumdf = ds.to_dataframe().reset_index().describe()
        assert 'time' in sumdf.columns
        assert 'altitude' in sumdf.columns
        assert 'derived_ozone' in sumdf.columns
        assert ds.sizes['time'] > 0
        assert ds.sizes['altitude'] > 0


def test_to_dataset_product_type4():
    _test_product('UAH', '4')


def test_to_dataset_product_type5():
    _test_product('NASA JPL TMTOL', '5')


def test_to_dataset_product_type8():
    try:
        _test_product('NASA JPL TMTOL', '8')
        raise KeyError('product_type=8 worked and should not have')
    except IOError:
        pass
