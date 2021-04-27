import numpy as np
import pandas as pd
import random

def intersection_along_given_axis(df,ax):
    lower = df[[f"{ax}_min_x", f"{ax}_min_y"]].max(axis=1)
    upper = df[[f"{ax}_max_x", f"{ax}_max_y"]].min(axis=1)
    overlap = upper - lower
    m = overlap < 0
    overlap[m] = 0

    return overlap

def jaccard(df):
    x_intersection = intersection_along_given_axis(df,"x")
    y_intersection = intersection_along_given_axis(df,"y")

    intersection_area = x_intersection*y_intersection

    area1 = (df["x_max_x"] - df["x_min_x"])*(df["y_max_x"] - df["y_min_x"])
    area2 = (df["x_max_y"] - df["x_min_y"]) * (df["y_max_y"] - df["y_min_y"])

    union_area = area1+area2-intersection_area

    j = intersection_area/union_area
    return j


def compare(a, b):
    m1 = a < 250
    m2 = b < 250

    t1 = np.sum(np.logical_and(m1, m2).astype(int), axis=(1, 2))
    t2 = np.sum(np.logical_and(~m1, m2).astype(int), axis=(1, 2))
    t3 = np.sum(np.logical_and(m1, ~m2).astype(int), axis=(1, 2))

    return t1 / (t1 + t2 + t3)


def estimate(tile_df, tiles, max_samples=None, user_df=None, user_tiles=None):
    estimations = dict()

    for character in tile_df["character"].unique():
        if user_df is not None:
            character_df = user_df[user_df["character"] == character]
            s = character_df.shape[0]
            t = user_tiles[character_df.index,:,:]
        else:
            s = 0
            t = None

        character_df = tile_df[tile_df["character"] == character]

        # if a maximum sample size has been met, take an additional tiles from the tesseract set
        if max_samples is not None:
            to_add = max(0,max_samples-s)
            indices = list(character_df.index)
            random.shuffle(indices)

            indices = indices[:to_add]
        else:
            indices = character_df.index

        t2 = tiles[indices]

        # do we have tiles from both user input and tesseract that need to be combined?
        if (t is not None) and (t2.shape[0] > 0):
            t = np.concatenate([t,t2])
        # we have only tesseract tiles
        elif t2.shape[0] > 0:
            t = t2
        # we have enough tiles from user input that we don't need anymore
        else:
            assert t is not None

        m = np.median(t, axis=0)
        estimations[character] = m

    return estimations

def calculate_confidence(glyph_estimation_dict: dict,tile_df,tile_images):
    glyph_confidence = []

    for character,glyph_estimate in glyph_estimation_dict.items():
        df = pd.DataFrame({"character": tile_df["character"]})
        df["similarity"] = compare(tile_images, glyph_estimate)

        df2 = df.sort_values("similarity", ascending=False).head(100)
        df3 = df2[df2["character"] == character]
        confidence = df3.shape[0] / 100

        glyph_confidence.append(({"character": character, "confidence": confidence}))

    glyph_confidence = pd.DataFrame(glyph_confidence)
    return glyph_confidence
