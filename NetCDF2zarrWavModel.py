#------------------------------------------------------------------------------------------------------------------
# Convertion from netcdf to zarr_store using xarray and zarr
# --------------------------------------------------------------------------------------------------------------------
#
#
#
#-----------------------------------------------------------------------------------------------------------------------'''

import argparse
from dask.distributed import Client, progress, LocalCluster
import pandas as pd
from pathlib import Path
import dask.array
import pyarrow.parquet as pq
import xarray as xr
import numpy as np
import numcodecs
import zarr
from datetime import datetime
import time
import sys

if __name__ == "__main__":

    numcodecs.blosc.use_threads = False

    # Read arguments from STDIN
    # batch_size is given in seconds, number_batches_to_append - number of time steps
    # start_time is initial time given by user in format "dd/mm/yy HH:MM:SS"

    # get base directory
    parser = argparse.ArgumentParser()
    parser.add_argument(
               "--basedir",
               default=".",
               help=("Base directory where the data dirs will be found." "\nDefaults to $PWD."),
    )
    #parser.add_argument('start_time',
    #                    type = mkdate,
    #                    help = ("Start time in the format dd/MM/yy HH:mm:SS")
    #)
    #parser.add_argument(
    #           'numbatches',
    #           type = int,
    #           help=("number of branches for chunk"),
    #)
    #parser.add_argument(
    #           'batchsize',
    #           type = int,
    #           help = ("batch size"),
    #)

    args = parser.parse_args()
    base_dir = Path(args.basedir)

    #    number_batches_to_append = int(args.numbatches)
    #batch_size = int(args.batchsize)
    #start_time = str(args.start_time)'''

    # set input and output paths
    service_id = "GLOBAL_ANALYSIS_FORECAST_WAV_001_027-TDS"
    product_id = "global-analysis-forecast-wav-001-027"
    path_in_dir = base_dir / product_id / "nc"
    path_out_dir = base_dir / product_id

    # make sure the output dir exists
    path_out_dir.mkdir(parents=True, exist_ok=True)

    # set list of variables
    variables=["VPED", "VSDX", "VSDY"]

    # convert files in nc directory to dataset using xarray
    nc_ds = xr.open_mfdataset(input_files, parallel=True, concat_dim="time", data_vars="minimal",combine='nested')

    start_day = pd.to_datetime(nc_ds.time.min().values)
    end_day = pd.to_datetime(nc_ds.time.max().values)
    end_day =datetime(end_day.year,end_day.month,end_day.day+1)

    # set zarr store name
    for variable_name in variables:
        # select files containing variable {variable_name}
        input_files = sorted(path_in_dir.glob(f"*{variable_name}*.nc"))

        # convert files in nc directory to dataset using xarray
        nc_ds = xr.open_mfdataset(input_files, parallel=True, concat_dim="time", data_vars="minimal",combine='nested')

        # define zarr store name according to convention {product_id}/{product_id}_{variable_name}_{start_day}_{end_day}.zarr
        zar_store = f"{product_id}/{product_id}_{variable_name}_{start_day}_{end_day}.zarr"

        # convert dataset to zarr
        nc_ds.to_zarr(zar_store, mode="w")
