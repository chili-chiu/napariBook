from myst_nb import glue
import napari
from napari.utils import nbscreenshot
from skimage import data

# load multichannel image in one line, with additional options
viewer = napari.view_image(data.cells3d(), channel_axis=1, name=["membrane", "nuclei"], colormap=["green", "magenta"])
viewer.dims.ndisplay = 3

s1 = nbscreenshot(viewer)
glue("s1",s1)