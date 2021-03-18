import re
import os
import pandas as pd
import cv2
import numpy as np


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

    return tile_df,tile_images

