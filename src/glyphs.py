import numpy as np
import pandas as pd

def compare(a, b):
    m1 = a < 250
    m2 = b < 250

    t1 = np.sum(np.logical_and(m1, m2).astype(int), axis=(1, 2))
    t2 = np.sum(np.logical_and(~m1, m2).astype(int), axis=(1, 2))
    t3 = np.sum(np.logical_and(m1, ~m2).astype(int), axis=(1, 2))

    return t1 / (t1 + t2 + t3)


def estimate(tile_df, tile_images, max_samples=None, user_df=None, user_images=None):
    estimations = dict()

    for character in tile_df["character"].unique():
        character_df = tile_df[tile_df["character"] == character]

        m = np.median(tile_images[character_df.index, :, :], axis=0)
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
