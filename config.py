settings = dict(
    number_of_games = 10,
    load_model=False,
    color = 'black', # black or white
    bot_level = 1, # 1 or 2,
    show_debug=False,
    save_games=False,
    checkpoint_location='checkpoints\\model_weights.h5',
    dataset_location='datasets\\othello_dataset.csv',
    xml_location='datasets\\othello_xml.xml',
    my_games_location='datasets\\othello_self_games.csv'
)

model = dict(
    model_type='vgg19',
    batch_size = 32, # 32
    epochs = 20, # 20
    max_loaded_matches = 400, # 1500, 1000
    split_validation = 0.8
)