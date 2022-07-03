settings = dict(
    number_of_games = 1,
    load_model=True,
    color = 'black', # black or white
    bot_level = 2,
    show_debug=True,
    save_games=False,
    checkpoint_location='checkpoints\\main.h5',
    dataset_location='datasets\\othello_dataset.csv',
    xml_location='datasets\\othello_xml.xml',
    my_games_location='datasets\\othello_self_games.csv'
)

model = dict(
    model_type='4conv',
    batch_size = 32, # 32
    epochs = 25, # 20
    max_loaded_matches = 1500, # 1500, 1000
    split_validation = 0.8
)