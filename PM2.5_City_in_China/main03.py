import os
import pandas as pd
import numpy as np
import config
import mpld3
from mpld3 import plugins
from pyecharts import Bar

def main():
    # === Step 5. Visualization ===
    comp_df = pd.read_csv(os.path.join(config.output_path, 'comparison_result.csv'), index_col=0)
    print(comp_df.head())

    good_res = comp_df.iloc[0, :].values
    heavy_res = comp_df.iloc[1, :].values
    light_res = comp_df.iloc[2, :].values
    medium_res = comp_df.iloc[3, :].values

    labels = comp_df.index.values.tolist()
    city_names = comp_df.columns.tolist()

    bar = Bar("Stacked bar chart")
    bar.add('Good', city_names, good_res, is_stack=True, xaxis_interval=0, xaxis_rotate=30)
    bar.add('Light', city_names, light_res, is_stack=True, xaxis_interval=0, xaxis_rotate=30)
    bar.add('Medium', city_names, medium_res, is_stack=True, xaxis_interval=0, xaxis_rotate=30)
    bar.add('Heavy', city_names, heavy_res, is_stack=True, xaxis_interval=0, xaxis_rotate=30)

    bar.render(os.path.join(config.output_path, 'echarts_comparison_result.html'))

if __name__ == '__main__':
    main()
