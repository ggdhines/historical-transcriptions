import re
import os
import pandas as pd
import cv2
import numpy as np
from sklearn.model_selection import train_test_split


def upload_to_db(latent_df, split_label, tesseract_model_version, cvae_model_version, engine):
    # just to make sure that we don't overwrite existing values
    df = latent_df

    # we will want to store results for both the testing and training sets
    df["split"] = split_label
    # in case we want to try different models (e.g. rebalanced sampling)
    # need to store somewhere that cave_model = 0 => base, and tesseract_model = 0 > eng
    # but by having numerical values, we can find the most recent models
    df["cvae_model"] = cvae_model_version
    # the tesseract language model also affects the tiles
    df["tesseract_model"] = tesseract_model_version

    columns = ["file_prefix",
               "local_tile_index",
               "most_likely_character",
               "confidence",
               "cvae_model",
               "tesseract_model",
               "split"]

    df[columns].to_sql("cvae_results", engine, if_exists="append", index=False)

def quick_tile_filter(tile_df,required_darkness,minimum_size,maximum_size):
    m1 = tile_df["darkest_pixel"] <= required_darkness

    m2 = tile_df["area"] <= maximum_size
    m3 = tile_df["area"] >= minimum_size

    # DO NOT reset index!!
    return tile_df[m1 & m2 & m3]


def split(df,images):
    train_df,test_df = train_test_split(df, test_size=0.25, random_state=0)

    train_images = images[train_df.index]
    # we no longer need this index wrt to the original dataframe
    train_df = train_df.reset_index(drop=True)

    test_images = images[test_df.index]
    test_df = test_df.reset_index(drop=True)

    train_images = train_images / 255
    test_images = test_images / 255

    # sanity check
    assert np.max(train_images) == 1
    return train_images,test_images,train_df,test_df


def load_user_results(engine,directory):
    """
    :param engine: to connect to the sql database
    :param directory: we still need to know where the images are stored
    :return:
    """
    stmt = "select * from user_results"
    user_tiles = pd.read_sql(stmt, engine)

    tiles_to_return = []
    sorted_df = []

    for file_prefix in user_tiles["file_prefix"].unique():
        image_fname = directory+file_prefix+"_ocr_ready.png"

        m1 = user_tiles["file_prefix"] == file_prefix

        tiles,meta_data = extract_tiles_from_image(image_fname,user_tiles[m1])

        df = pd.concat([user_tiles[m1].reset_index(drop=True),meta_data],axis=1)
        tiles_to_return.extend(tiles)
        sorted_df.append(df)

    sorted_df = pd.concat(sorted_df)
    tiles_to_return = np.asarray(tiles_to_return)

    return sorted_df,tiles_to_return

def extract_tiles_from_image(image_fname,tile_df):
    """
    extract the actual tile images for each for in the given df as well as some additional useful information
    :param image:
    :param tile_df:
    :return:
    """
    max_darkness = []
    tiles = []

    image = cv2.imread(image_fname, 0)

    for _, row in tile_df.iterrows():
        tile = image[row.y_min:row.y_max, row.x_min:row.x_max]
        resized_tile = cv2.resize(tile, (28, 28))
        max_darkness.append(np.min(tile))
        tiles.append(resized_tile)

    area = (tile_df["x_max"] - tile_df["x_min"]) * (tile_df["y_max"] - tile_df["y_min"])

    tile_metainfo = pd.DataFrame({"area": area, "max_darkness": max_darkness}).reset_index(drop=True)
    return tiles,tile_metainfo

def load_tesseract_results(directory):
    tile_df = []
    tile_images = []

    # search for all images which we have run through Tesseract
    for fname in os.listdir(directory):
        match = re.search("(.*)-(\d+)-(\d+)\-(\d*)_ocr_ready.png", fname)
        if match is None:
            continue

        print(fname, end="\r")

        csv_file = fname[:-13] + "ocr.csv"

        tiles_on_page = pd.read_csv(directory + csv_file, delimiter=" ", error_bad_lines=False, engine="python", quoting=3)
        # Because there are several reserved name conflicts in both SQL and Javascript/HTML
        # todo - get rid of top etc. in the first place
        tiles_on_page = tiles_on_page.rename(columns={"top": "y_min",
                                                      "bottom": "y_max",
                                                      "left": "x_min",
                                                      "right": "x_max"})
        tiles,tile_metainfo = extract_tiles_from_image(directory+fname, tiles_on_page)

        # add the additional metainfo for each tile
        tiles_on_page = pd.concat([tiles_on_page,tile_metainfo],axis=1)
        tiles_on_page["file_prefix"] = fname[:-14]

        try:
            tiles_on_page["ship_name"] = match.groups()[0]
            tiles_on_page["year"] = int(match.groups()[1])
            tiles_on_page["month"] = int(match.groups()[2])
            tiles_on_page["page_number"] = int(match.groups()[3])
        except ValueError:
            print(match.groups())
            raise

        tiles_on_page["local_tile_index"] = tiles_on_page.index

        tile_df.append(tiles_on_page)

        tile_images.extend(tiles)

    tile_df = pd.concat(tile_df, ignore_index=True)

    tile_df["model"] = 0
    tile_df = tile_df.rename(columns={})

    tile_images = np.asarray(tile_images)
    s = tile_images.shape

    # todo - think this reshape is only needed for CVAE
    # tile_images = tile_images.reshape((s[0], s[1], s[2], 1))


    return tile_df, tile_images

