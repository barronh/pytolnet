__all__ = ['TOLNetAPI']
__doc__ = """TOLNet API
==========

Utilities for retrieving and plotting TOLNet data.

To Install
----------

.. code-block:: bash

    python -m pip install --user git+https://github.com/barronh/pytolnet.git

Example
-------

.. code-block:: python

    import pytolnet
    api = pytolnet.TOLNetAPI()
    cldf = api.data_calendar('UAH')
    newest_data_id = cldf.index.values[0]
    ds = api.to_dataset(newest_data_id)
    print(ds.to_dataframe().reset_index().describe())
    #                                 time      altitude  derived_ozone
    # count                         174096  174096.00000   63538.000000
    # mean   2023-08-16 19:17:36.874643968       7.72500      48.525455
    # min              2023-08-16 13:06:59       0.30000       0.015444
    # 25%              2023-08-16 16:10:39       4.01250      40.799999
    # 50%              2023-08-16 19:18:37       7.72500      47.500000
    # 75%              2023-08-16 22:24:22      11.43750      55.299999
    # max              2023-08-17 01:31:57      15.15000     100.000000
    # std                              NaN       4.29549      13.209246
"""
__version__ = '0.1.1'

changelog = """
v0.1.0 : First release. Includes fix for boolean properties.
"""


class TOLNetAPI:
    def __init__(
        self, token='anonymous', cache='.',
        root='https://tolnet.larc.nasa.gov/api'
    ):
        """
        Arguments
        ---------
        token : str
            token for API if using non-anonymous access.
        root : str
            Path to TOLNet API
        Returns
        -------
        api : TOLNetAPI
            Object for accessing TOLNetAPI

        Example
        -------

        .. code-block:: python

            import pytolnet
            api = pytolnet.TOLNetAPI()
            cldf = api.data_calendar('UAH')
            newest_data_id = cldf.index.values[0]
            ds = api.to_dataset(newest_data_id)
            print(ds.to_dataframe().reset_index().describe())
            #                                 time      altitude  derived_ozone
            # count                         174096  174096.00000   63538.000000
            # mean   2023-08-16 19:17:36.874643968       7.72500      48.525455
            # min              2023-08-16 13:06:59       0.30000       0.015444
            # 25%              2023-08-16 16:10:39       4.01250      40.799999
            # 50%              2023-08-16 19:18:37       7.72500      47.500000
            # 75%              2023-08-16 22:24:22      11.43750      55.299999
            # max              2023-08-17 01:31:57      15.15000     100.000000
            # std                              NaN       4.29549      13.209246
        """
        import requests
        self._session = requests.Session()
        self._root = root
        self.set_token(token)
        self._instrument_groups_df = None
        self._file_types_df = None
        self._product_types_df = None
        self._processing_types_df = None
        self._cache = cache

    def set_token(self, token=None):
        """
        Arguments
        ---------
        token : str
            Token to use for access. Use 'anonymous' if you don't have one.
            Use None if you want to be prompted
        """
        import getpass
        if token is None:
            prompt = (
                'Enter token for authorized access or anonymous if you do not'
                + ' have a token\nEnter token:'
            )
            token = getpass.getpass(prompt)

        self._token = token
        self._headers = {"Authorization": f"Bearer {token}"}

    def _get_meta(self, key, params=None):
        """
        Simple wrapper to open and return a dataframe
        """
        import pandas as pd
        if params is None:
            params = {}
        root = self._root
        headers = self._headers
        s = self._session
        r = s.get(f'{root}/{key}', headers=headers, params=params)
        j = r.json()
        if 'status' in j and 'message' in j:
            raise IOError('Status {status}: {message}'.format(**j))
        df = pd.DataFrame.from_records(j)
        if 'id' in df.columns:
            df = df.set_index('id').sort_index()
        return df

    def instruments_groups(self):
        """
        Returns
        -------
        igdf : pandas.DataFrame
            Instrument groups dataframe
        """
        if self._instrument_groups_df is None:
            self._instrument_groups_df = self._get_meta('instruments/groups')
        return self._instrument_groups_df

    def product_types(self):
        """
        Returns
        -------
        prdf : pandas.DataFrame
            Product types dataframe
        """
        if self._product_types_df is None:
            self._product_types_df = self._get_meta('data/product_types')
        return self._product_types_df

    def file_types(self):
        """
        Returns
        -------
        fldf : pandas.DataFrame
            File types dataframe
        """
        if self._file_types_df is None:
            self._file_types_df = self._get_meta('data/file_types')
        return self._file_types_df

    def processing_types(self):
        """
        Returns
        -------
        ptdf : pandas.DataFrame
            Processing types dataframe
        """
        if self._processing_types_df is None:
            self._processing_types_df = self._get_meta('data/processing_types')
        return self._processing_types_df

    def data_calendar(
        self, igname=None, igid=None, product_type='4', processing_type=None,
        file_type='1', ascending=False
    ):
        """
        Retrieve a data calendar.

        Arguments
        ---------
        igname : str or None
            Instruments Group name (see instruments_group)
        igid : int or None
            Instruments Group id (see instruments_group); supersedes igname.
            If igname and igid are None, returns calendar from all instruments
        product_type : int or str
            Defaults to 4 (HIRES), which is the supported data to be read.
            Other formats (5=CALVAL; 6=CLIM) are not tested. Remaining formats
            (7=gridded; 8=legacy) not likely to work.
        processing_type : int or str
            Defaults to '1,2' (central,inhouse). Unprocessed (3) is not yet
            supported.
        file_type : int or str
            Defaults to '1' (HDF GEOMS). See file_types for other options.

        Returns
        -------
        caldf : pandas.DataFrame
            DataFrame of data by date

        Example
        -------

        .. code-block:: python

            import pytolnet
            api = pytolnet.TOLNetAPI()
            cldf = api.data_calendar('UAH')
            print(cldf.columns)
            # 'start_data_date', 'public', 'near_real_time', 'isAccessible'

        """
        from warnings import warn
        import pandas as pd

        if igid is None:
            igdf = self.instruments_groups()
            if igname is None:
                cldfs = []
                opts = dict(
                    product_type=product_type, processing_type=processing_type,
                    file_type=file_type, ascending=ascending
                )
                for igid, row in igdf.iterrows():
                    try:
                        cldfs.append(self.data_calendar(igid=igid, **opts))
                    except Exception as e:
                        instrument_group_name = row['instrument_group_name']
                        msg = f'igid={igid} failed ({instrument_group_name})'
                        msg += f'; {e}'
                        warn(msg)
                return pd.concat(cldfs)
            else:
                sigdf = igdf.query(f'instrument_group_name == "{igname}"')
                if sigdf.shape[0] == 0:
                    ignames = igdf['instrument_group_name'].unique()
                    raise KeyError(f'igname not in {ignames}; got {igname}')
                igids = sigdf.index.values
                igid = igids[0]
                if sigdf.shape[0] > 1:
                    warn(f'igname is not unique {igids}; defaulting to {igid}')

        params = dict(
            instrument_group=igid, product_type=product_type,
            file_type=file_type
        )
        if processing_type is not None:
            params['processing_type'] = processing_type
        cldf = self._get_meta('data/calendar', params=params)
        return cldf.sort_values('start_date', ascending=ascending)

    def to_dataset(self, id, cache=None, overwrite=False, product_type=4):
        """
        Acquire data from product_type and return it as an xarray.Dataset

        Arguments
        ---------
        id : int
            Must come from data with product_type=4
        cache : str
            Path to keep cahed files
        overwrite : bool
            If False (default), use cached files in cache folder.
            If True, remake all files
        product_type : int
            Currently supports 4, 5 and 6 (all same)

        Returns
        -------
        ds : xarray.Dataset
            Dataset for file requested

        Example
        -------

        .. code-block:: python

            import pytolnet
            api = pytolnet.TOLNetAPI()
            ds = api.to_dataset(2115)

        """
        opts = dict(id=id, cache=cache, overwrite=overwrite)
        if product_type == 4:
            ds = self.get_product_type4(**opts)
        elif product_type == 5:
            ds = self.get_product_type5(**opts)
        elif product_type == 6:
            ds = self.get_product_type6(**opts)
        else:
            raise IOError(f'Only supports product_type=4, got {product_type}')
        return ds

    def get_product_type6(self, id, cache=None, overwrite=False):
        """
        Product type 6 has the same format as 4, so this is a thin wrapper.

        Same as to_dataset(..., product_type=5)
        """
        opts = dict(id=id, cache=cache, overwrite=overwrite)
        return self.get_product_type4(**opts)

    def get_product_type5(self, id, cache=None, overwrite=False):
        """
        Product type 5 has the same format as 4, so this is a thin wrapper.

        Same as to_dataset(..., product_type=5)
        """
        opts = dict(id=id, cache=cache, overwrite=overwrite)
        return self.get_product_type4(**opts)

    def get_product_type4(self, id, cache=None, overwrite=False):
        """
        Acquire data from product_type=4 and return it as an xarray.Dataset
        Same as to_dataset(..., product_type=4)

        Arguments
        ---------
        id : int
            Must come from data with product_type=4
        cache : str
            Path to keep cahed files
        overwrite : bool
            If False (default), use cached files in cache folder.
            If True, remake all files

        Returns
        -------
        ds : xarray.Dataset
            Dataset for file requested
        """
        import numpy as np
        import pandas as pd
        import xarray as xr
        import os

        root = self._root
        headers = self._headers
        s = self._session
        if cache is None:
            cache = self._cache

        outpath = f'{cache}/{id}.nc'
        if not os.path.exists(outpath) or overwrite:
            r = s.get(f'{root}/data/json/{id}', headers=headers)
            j = r.json()
            altattrs = j['altitude']['attributes']
            altattrs = {k[4:].lower(): v for k, v in altattrs.items()}
            altdata = np.array(j['altitude']['data'])
            alt = xr.DataArray(
                altdata, name='altitude', dims=('altitude'), attrs=altattrs
            )
            timeattrs = j['datetime']['attributes']
            timeattrs = {k[4:].lower(): v for k, v in timeattrs.items()}
            timeattrs['units'] = 'seconds since 1970-01-01 00:00:00+0000'
            timedata = (
                pd.to_datetime(j['datetime']['data'])
                - pd.to_datetime('1970-01-01 00:00:00+0000')
            ).total_seconds()
            time = xr.DataArray(
                timedata, name='time', dims=('time'), attrs=timeattrs
            )
            varattrs = j['value']['attributes']
            varattrs = {k[4:].lower(): v for k, v in varattrs.items()}
            vardata = np.array(j['value']['data']).astype('f')
            vardata = np.ma.masked_values(vardata, varattrs['fill_value'])
            vardata = np.ma.masked_greater(vardata, varattrs['valid_max'])
            vardata = np.ma.masked_less(vardata, varattrs['valid_min'])
            var = xr.DataArray(
                vardata, dims=('time', 'altitude'),
                name='derived_ozone',
                coords={'time': time, 'altitude': alt},
                attrs=varattrs
            )
            fattrs = {k: v for k, v in j['attributes'].items()}
            fattrs.update({
                k: v for k, v in j.items()
                if k not in (
                    'altitude', 'datetime', 'value', 'attributes', 'fileInfo'
                )
            })
            fileinfo = {
                k: v if not isinstance(v, bool) else int(v)
                for k, v in j['fileInfo'].items()
            }
            fattrs.update(fileinfo)
            vds = xr.Dataset(data_vars={'derived_ozone': var}, attrs=fattrs)
            vds.to_netcdf(outpath)
        ds = xr.open_dataset(outpath)
        return ds
