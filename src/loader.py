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


def load_tesseract_results(directory):
    tile_df = []
    tile_images = []

    for fname in os.listdir(directory):
        match = re.search("(.*)-(\d+)-(\d+)\-(\d*)_ocr_ready.png", fname)
        if match is None:
            continue

        print(fname, end="\r")

        csv_file = fname[:-13] + "ocr.csv"
        img = cv2.imread(directory + fname, 0)

        tiles_on_page = pd.read_csv(directory + csv_file, delimiter=" ", error_bad_lines=False, engine="python", quoting=3)

        #     m1 = tiles["confidence"] > 95
        #     tiles = tiles[m1]

        max_darkness = []
        for _, row in tiles_on_page.iterrows():
            tile = img[row.top:row.bottom, row.left:row.right]
            resized_tile = cv2.resize(tile, (28, 28))
            max_darkness.append(np.min(tile))
            tile_images.append(resized_tile)

        tiles_on_page["darkest_pixel"] = max_darkness
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

    tile_df = pd.concat(tile_df, ignore_index=True)
    tile_df["area"] = (tile_df["right"] - tile_df["left"]) * (tile_df["bottom"] - tile_df["top"])
    tile_df["model"] = 0
    tile_df = tile_df.rename(columns={})

    tile_images = np.asarray(tile_images)
    s = tile_images.shape
    tile_images = tile_images.reshape((s[0], s[1], s[2], 1))

    # Because there are several reserved name conflicts in both SQL and Javascript/HTML
    tile_df = tile_df.rename(columns={"top": "y_min", "bottom": "y_max", "left": "x_min", "right": "x_max"})
    return tile_df, tile_images

