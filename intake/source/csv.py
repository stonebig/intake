from . import base


class Plugin(base.Plugin):
    """
    Creates CSVSource objects
    """
    def __init__(self):
        super(Plugin, self).__init__(name='csv', version='0.1',
                                     container='dataframe',
                                     partition_access=True)

    def open(self, urlpath, **kwargs):
        storage_options = kwargs.pop('storage_options', None)
        base_kwargs, source_kwargs = self.separate_base_kwargs(kwargs)
        return CSVSource(urlpath=urlpath, csv_kwargs=source_kwargs,
                         metadata=base_kwargs['metadata'],
                         storage_options=storage_options)


# For brevity, this implementation just wraps the Dask dataframe
# implementation. Generally, plugins should not use Dask directly, as the
# base class provides the implementation for to_dask().
class CSVSource(base.DataSource):
    """Read CSV files into dataframes

    Parameters
    ----------
    urlpath: str, location of data
        May be a local path, or remote path if including a protocol specifier
        such as ``'s3://'``. May include glob wildcards.
    csv_kwargs: dict
        Any further arguments to pass to Dask's read_csv (such as block size)
        or to the `CSV parser <https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html>`_
        in pandas (such as which columns to use, encoding, data-types)
    storage_options: dict
        Any parameters that need to be passed to the remote data backend,
        such as credentials.
    """

    def __init__(self, urlpath, csv_kwargs, metadata, storage_options=None):
        self._urlpath = urlpath
        self._storage_options = storage_options
        self._csv_kwargs = csv_kwargs
        self._dataframe = None

        super(CSVSource, self).__init__(container='dataframe',
                                        metadata=metadata)

    def _get_schema(self):
        import dask.dataframe

        if self._dataframe is None:
            self._dataframe = dask.dataframe.read_csv(
                self._urlpath, storage_options=self._storage_options,
                **self._csv_kwargs)

        dtypes = self._dataframe._meta
        return base.Schema(datashape=None,
                           dtype=dtypes,
                           shape=(None, len(dtypes.columns)),
                           npartitions=self._dataframe.npartitions,
                           extra_metadata={})

    def _get_partition(self, i):
        return self._dataframe.get_partition(i).compute()

    def _close(self):
        self._dataframe = None
