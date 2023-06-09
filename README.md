# Fabulous-Feathers

This is Fabulous Feathers, a parametric software tool for Fused Filament Fabrication (FFF) 3D-printed hair structures embodied in a feather. With the use of the Full Control Python library, a software tool was created through which a variety of 3D-printable feather designs can be generated. The feather serves as a proof of concept for the printing of fine hair structures at home, as well as a demonstrator of the design possibilities of Full Control. 
Traditionally, the design pipeline for FFF 3D printing involves going back and forth between CAD, slicer and printing to achieve the desired result. Full Control enables precise control of the printing process, allowing fine details to be printed successfully and more effectively eliminating errors in the design, by veering from the traditional pipeline.
In contrast to the existing literature about 3D-printed FFF wearable materials, this project demonstrates a fully open-source parametric FFF design, enabling other designers to replicate the design. It is a contemporary example of 3D-printable open-source design for the design community.

Don't want to install anything on your machine? Make Google run it for you in [Colab](https://colab.research.google.com/github/FrostiFish/Fabulous-Feathers/blob/main/Fabulous%20Feathers.ipynb#)!

This design is created using Python, Jupyter Notebook and [Full Control](https://github.com/FullControlXYZ/fullcontrol). For a robust and easy way to manage Python environments, I recommend [Anaconda](https://www.anaconda.com/). To install Full Control, follow the instructions in their GitHub repository, or simply install it using this repository's provided Conda Enviroment. For a comprehensive guide on importing and managing Python environments using Anaconda, check out [Managing Environments](https://docs.anaconda.com/free/navigator/tutorials/manage-environments/). You can also install the requirement using pip. Navigate the Fabulous Feathers directory and run `pip install -r requirements.txt`

To print your own feather, follow the steps in the Fabulous Feathers.ipynb.  
If you want to achieve a more natural look as shown in the project [video](https://www.reddit.com/r/FullControl/comments/146byi5/fabulous_feathers_4d_printing_feathers_based_on/), submerging the feather in 80 degrees Celcius water for 5 seconds should to the trick (be careful not to burn your hands of course!). The moment you take it out of the water, the barbs and rachis will start to deform. There is no one way to go about this though, every feather will turn out unique, so have fun and be creative. :)

This project is in early access. Contributing is highly encouraged! Create a fork and submit a pull request if you have any proposal to add or change functionality.
