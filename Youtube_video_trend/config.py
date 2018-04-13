import os

dataset_path = './data'
output_path = './output'

if not os.path.exists(output_path):
    os.makedirs(output_path)

countries = ['CA', 'DE', 'GB', 'US']
usecols = ['video_id', 'trending_date', 'channel_title', 'category_id', 'publish_time', 'views', 'likes',
           'dislikes', 'comment_count', 'comments_disabled', 'ratings_disabled', 'video_error_or_removed'']
