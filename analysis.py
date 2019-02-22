import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from skimage.segmentation import clear_border, felzenszwalb
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
from skimage.util import img_as_float
from skimage.io import imread
from skimage.color import label2rgb

def segment_image(img, scale=500, sigma=0.5, min_size=30, min_area=30):
    image = img_as_float(img)

    # Run the segmentation algorithm
    segments_fz = felzenszwalb(image, scale=scale, sigma=sigma, min_size=min_size)

    # remove artifacts connected to image border
    cleared = clear_border(segments_fz)

    # label image regions
    label_image = label(cleared)

    return list(filter(lambda region: region.area >= min_area, regionprops(label_image)))

def draw(img, regions):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(img)

    for i, region in enumerate(regions):
        # draw rectangle around segmented coins
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                fill=False, edgecolor='green', linewidth=2)
        ax.add_patch(rect)

    ax.set_axis_off()
    plt.tight_layout()
    fig.canvas.draw()