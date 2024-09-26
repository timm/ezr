python3.13 -B filter_data.py ../data/optimize/[chmp]*/*.csv > tmp
grep -e "high" -e "dim" -e "----" tmp > high_dim_datasets.txt
grep -e "low" -e "dim" -e "----" tmp > low_dim_datasets.txt
rm tmp