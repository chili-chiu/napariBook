#!/usr/bin/env python
# coding: utf-8

# # 3D molecules in cells

# ## Summary
# 
# This tutorial uses napari 0.4.12.<br>
# 
# Dataset:<br>
# scikit-image > Cells (3D+2Ch)
# 
# Analysis goals:<br> 
# Count the number of points per cell.
# 
# Steps:
# - Load image
# - Cell segmentation
# - Points detection
# - Quantify number of points per cell
# - Plot number of points versus cell size

# In[1]:


import napari
from napari.utils import nbscreenshot
from skimage import data

viewer = napari.view_image(data.cells3d(), channel_axis=1, name=["membrane", "nuclei"], colormap=["green", "magenta"])
viewer.dims.ndisplay = 3

#Reload the saved label layer if necessary
from tifffile import imread
viewer.add_labels(imread(file_name), name = 'seg')

from myst_nb import glue
s1 = nbscreenshot(viewer)
glue("s1",s1)


# ## Load Image
# 
# Use skimage.data.cells3d as the example image.<br>
# The original image has dimension ZCYT=(60, 2, 256, 256). Load each channel as an image layer for easier display and downstream process.
# 

# ````{tabbed} napari in code
# 
# ```python
# #load multichannel image in one line, with additional options
# viewer = napari.view_image(data.cells3d(), channel_axis=1, name=["membrane", "nuclei"], colormap=["green", "magenta"])
# viewer.dims.ndisplay = 3
# ```
# 
# ````
# 
# ````{tabbed} napari in GUI gif
# ![SegmentLocal](file_open.gif "segment")
# ````

# ## Cell segmentation
# 
# Use Cellpose to segment cells, with following settings for faster calculation:<br>
# image layer = nuclei<br>
# model type = nuclei<br>
# click "compute diameter from image"<br>
# uncheck "average 4 nets", "output flows and cellprob", "output outlines", "resample dynamics"<br>
# check "process stack as 3D"<br>
# 
# Once done, use label eraser to manually clean up unwanted fragments from dividing nucleus.<br>
# 
# For more information, please see [napari labels layer](https://napari.org/tutorials/fundamentals/labels.html) and
# [Cellpose plugin](https://www.napari-hub.org/plugins/cellpose-napari).<br>

# {glue:}`s1`
# 
# ![seg](seg.png)

# ## Points detection
# 
# (1) Use skimage.feature.blob_log to detect points in membrane channel <br>
# (2) Add points layer named "aggregates" <br>
# 
# For more information, please see [napari points layer](https://napari.org/tutorials/fundamentals/points.html).<br>

# In[ ]:


from skimage.feature import blob_log

blobs = blob_log(viewer.layers['membrane'].data, min_sigma=0.35, max_sigma=1, num_sigma=10, threshold=0.6)
#returns coordinates + sigma, only keep coordinates
points = blobs[:,:-1]

viewer.add_points(points, size=2, name='aggregates')


# ````{tabbed} napari in code
# ```python
# from skimage.feature import blob_log
# 
# blobs = blob_log(viewer.layers['membrane'].data, min_sigma=0.35, max_sigma=1, num_sigma=10, threshold=0.6)
# #returns coordinates + sigma, only keep coordinates
# points = blobs[:,:-1]
# 
# viewer.add_points(points, size=2, name='aggregates')
# ```
# ````
# 
# ````{tabbed} napari in GUI
# place holder for future GUI gif
# ````

# ## Quantify number of points per cell
# 
# Use label layer value to identify points location.<br>

# In[10]:


import pandas as pd

cells = viewer.layers['seg'].data

#create a dataframe that contains points and their corresponding cell location
agg_cell = pd.DataFrame(columns=['z', 'y', 'x','cell'])
for agg in viewer.layers['aggregates'].data:
    z,y,x = agg.astype(int)
    agg_cell = agg_cell.append({'z':z,'y':y,'x':x,'cell':cells[z,y,x]},ignore_index=True) 

agg_count = agg_cell['cell'].value_counts().to_frame()
agg_count = agg_count.reset_index().rename(columns={'index':'cell','cell':'pt_count'})
print(agg_count)


# ## Plot number of points versus cell size

# In[12]:


import numpy as np
from skimage.measure import regionprops_table

properties = ['label', 'area']

cell_table = pd.DataFrame(regionprops_table(cells, properties=properties))
cell_table = cell_table.rename(columns={"label": "cell", "area": "size"})

#combine agg_count and cell_table
#columns: cell, pt_count, size
result = pd.merge(agg_count, cell_table, how="right", on=["cell"]).fillna(0)

#scatter plot: number of points versus cell size
import matplotlib.pyplot as plt
result.plot.scatter(x="size", y="pt_count")


# In[ ]:


viewer.close()

