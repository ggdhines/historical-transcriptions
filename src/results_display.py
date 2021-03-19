from matplotlib import pyplot as plt
import cv2
import numpy as np


directory = "/home/ggdhines/bear/"


def show_image(df, ideal_df, index):
    character = df.loc[index, ["character"]].values[0]

    m1 = df["character"] == character

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(121)
    df[m1].plot.scatter(x="mu", y="sigma", ax=ax)

    m2 = ideal_df["character"] == character
    ideal_df[m2].plot.scatter(x="mu", y="sigma", ax=ax, color="green", s=200)

    df.loc[index:index].plot.scatter(x="mu", y="sigma", ax=ax, color="red")

    print("Character is " + character)
    print(f"Ideal likelyhood is {ideal_df.loc[m2, 'likelyhood'].values}")
    print(f"Individual likelyhood is {df.loc[index:index, 'cvae_confidence'].values}")

    r = df.loc[index]
    file_name = directory + r["file_prefix"] + "-aligned.png"

    img = cv2.imread(file_name, 0)
    ax = fig.add_subplot(122)
    _ = ax.imshow(img[r["y_min"]:r["y_max"], r["x_min"]:r["x_max"]])
    plt.show()


def generate_character(model, x, y):
    s = np.array([x, y])
    s = s.reshape(1, 2)

    remapped = model.decode(s, apply_sigmoid=True)

    a = (np.array(remapped) * 255).astype(np.uint8)
    b = a.reshape((a.shape[1], a.shape[2]))
    ret2, th2 = cv2.threshold(b, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th2 = 255 - th2
    return th2


def generate_ideal(model, ideal_df, ch):
    r = ideal_df[ideal_df["character"] == ch]
    return generate_character(model, r["mu"], r["sigma"])