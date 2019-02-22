# CellCounter
This is a small GUI application for counting cells in microscope images.

## Requirements
CellCounter is written using PyQt5 and scikit-image, which are basically the only requirements. 

To run, install Miniconda, create new envirnment and install:
```
conda install -c anaconda numpy scikit-image pyqt
conda install -c conda-forge qimage2ndarray
```


## Usage
Set the parameters using the right sidebar. They correspons to the parameters of scikit-image felzenszwalb segmentation.
Click on the Analyze button to load an image. The algorithm will automatically analyze the image and display the result.

Using the mouse you can add and remove the found regions. 
Using left mouse button, you can create a rectangle and every region that intersects with that rectangle will be deleted.
On the other hand, use the right mouse button to draw new rectangles or just click it to create an average sized rectangle centered at the position where you clicked.

Once you are done, you can see the number of regions on the right. Moreover, you can save the final image using the Save button.