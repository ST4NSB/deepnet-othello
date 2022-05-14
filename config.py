settings = dict(
    number_of_games = 20,
    load_model=True,
    color = 'black', # black or white
    bot_level = 1, # 1 or 2,
    show_debug=True,
    save_games=False,
    checkpoint_location='checkpoints\\model_weights.h5',
    dataset_location='othello_dataset.csv',
    xml_location='othello_xml.xml',
    my_games_location='othello_self_games.csv'
)

model = dict(
    model_type='cnn',
    batch_size = 32,
    epochs = 20,
    max_loaded_matches = 1000,
    split_validation = 0.8
)