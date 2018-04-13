import os
import pandas as pd;
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pyecharts import Bar, Line, Overlap
import config


def get_category_from_json(json_file):

    category_dict = {}

    with open(json_file, 'r') as f:
        data = json.load(f)
        for category in data['items']:
            category_dict[int(category['id'])] = category['snippet']['title']
    return category_dict


def combine_video_data():

    videos_df_list = []

    for country in config.countries:
        video_df = pd.read_csv(os.path.join(config.dataset_path, country + 'videos.csv'), index_col='video_id', usecols=config.usecols)
        video_df['trending_date'] = pd.to_datetime(video_df['trending_date'], format='%y.%d.%m')
        video_df['publish_time'] = pd.to_datetime(video_df['publish_time'], format='%y-%m-%dT%H:%M:%S.%fZ')
        video_df['publish_date'] = video_df['publish_time'].dt.date
        video_df['publish_date'] = pd.to_datetime(video_df['publish_date'])

        category_dict = get_category_from_json(os.path.join(config.dataset_path, country + '_category_id.json'))
        video_df['category'] = video_df['category_id'].map(category_dict)
        video_df['country'] = country
        video_df_list.append(video_df)

        print('Preview of the data:')
        print(video_df.head())

    all_video_df = pd.concat(video_df_list)
    all_video_df.to_csv(os.path.join(config.output_path, 'all_videos.csv'))

    return all_video_df


def plot_top10_by_country(all_video_df, col_name, title, save_filename):

    fig, axes = plt.subplot(len(config.countries), figsize=(10, 8))
    fig.suptitle(title)

    for i, country in enumerate(config.countries):
        country_video_df = video_df[video_df['country'] == country]
        top10_df = country_video_df[col_name].value_counts().sort_values(ascending=False)[:10]
        x_labels = [label[:7] + '...' if len(label) > 10 else label for label in top10_df.index]
        sns.barplot(x=x_labels, y=top10_df.values, ax=axes[i])
        axes[i].set_xticklabels(x_labels, rotation=45)
        axes[i].set_title(country)
    plt.tight_layout()

    plt.subplot_adjust(top=0.9)
    plt.savefig(os.path.join(config.output_path, save_filename))
    plt.show()


def plot_days_to_trend(video_df, save_filename):

    video_df['diff'] = (video_df['trending_date'] - video_df['publish_date']).dt.days
    days_df = video_df['diff'].value_counts()

    days_df = days_df[(days_df.index >= 0) & (days_df.index <= 60)]
    days_df = days_df.sort_index()
    bar = Bar('Two months after videos are published:')
    bar.add('Bar chart', days_df.index.tolist(), days_df.values.tolist(),
            is_datazoom_show=True, datazoom_range=[0, 50])

    line = Line()
    line.add('Line chart', dayss_df.index.tolist(), days_df.values.tolist())

    overlap.Overlap()
    overlap.add(bar)
    overlap.add(line)
    overlap.render(os.path.join(config.output_path, save_filename))


def plot_relationship_of_cols(video_df, cols):

    sel_video_df = all_video_df[cols + ['country']]
    g = sns.pairplot(data=sel_video_df, hue='country')
    g.savefig(os.path.join(config.output_path, 'pair_plot.png'))
    plt.show()

    corr_df = sel_video_df.corr()
    sns.heatmap(corr_df, annot=True)
    plt.savefig(os.path.join(config.output_path, 'heat_map.png'))
    plt.show()


def main():

    all_video_df = combine_video_data()

    plot_top10_by_country(all_video_df, 'category', 'Top10 video categories of each country', 'top10_category')
    plot_top10_by_country(all_video_df, 'channel_title', 'Top10 video channels of each country', 'top10_channels')
    plot_days_to_trend(all_video_df, 'publish_vs_trend.html')

    cols = ['views', 'likes', 'dislikes', 'comment_count']
    plot_relationship_of_cols(all_video_df, cols)


if __name__ == '__main__':
    main()
