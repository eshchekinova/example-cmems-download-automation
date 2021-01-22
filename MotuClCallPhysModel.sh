#!/usr/bin/env bash

# read base dir (if any)
if [ $# -eq 0 ]; then
    echo "No arguments provided, will use $(pwd) as base dir."
    base_dir="$(pwd)"
else
    base_dir="$1"
fi

# parameters
name_dir_out_nc="${base_dir}/GLOBAL_ANALYSIS_FORECAST_PHY_NC"
name_file_out="GLOBAL_ANALYSIS_FORECAST_PHY_001_24-TDS"
service_id="GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS"
product_id="global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh"
lon_min=-180
lon_max=179.91667
lat_min=-80
lat_max=90
depth_min=0.493
depth_max=0.4942
times=("2021-01-23 21:00:00" "2021-01-23 21:30:00" "2021-01-23 21:30:00"  "2021-01-23 22:30:00")

# make sure the output dir exists
mkdir -p "${name_dir_out_nc}"

# loop over each time step and download the respective file
for i in "${!times[@]}";
do
  time_min=${times[$i]}
  time_max=$time_min
  time_stamp=$(echo "$time_min" | tr -s ' ' '_')
  name_file_out_nc="$name_file_out"_"$time_stamp"
  python3 -m motuclient \
    --motu http://nrt.cmems-du.eu/motu-web/Motu \
    --service-id "${service_id}" --product-id $product_id \
    --longitude-min $lon_min --longitude-max $lon_max \
    --latitude-min $lat_min --latitude-max $lat_max \
    --date-min "$time_min" --date-max "$time_max" \
    --depth-min $depth_min --depth-max $depth_max \
    --variable uo --variable vo \
    --out-dir "$name_dir_out_nc" --out-name "${name_file_out_nc}.nc" \
    --user "${MOTU_USER}" --pwd "${MOTU_PASSWORD}"
done
