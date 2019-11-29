# niicat

This is a tool to quickly preview nifti images on the terminal. 
This can be helpful if you are working on a remote server via SSH and do not have
a -X connection. It uses [libsixel](https://github.com/saitoha/libsixel) to display the images.
Niicat can also display png, jpg or similar images.


### Install:

```
pip install niicat
```


### Usage:

```
niicat T1.nii.gz
```

![](niicat/resources/example.gif)


### Possible problems

If nothing is displayed check if your [terminal supports sixel](https://github.com/saitoha/libsixel#terminal-requirements).

You might also encounter the following error message:
```
ctypes.ArgumentError: argument 2: <class 'TypeError'>: wrong type
```
This is a known [problem](https://github.com/fastai/fastai/issues/2170) when using libsixel-python. 
In this case try using niicat with the option `-ic` if you are using iterm2 (this will use `imgcat` from iterm2) or 
with the option `-lb` (this will use `libsixel-bin` which can be installed via `sudo apt install libsixel-bin`).

Niicat was only tested on python >= 3.5.


### License

Copyright © German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC).
Please make sure that your usage of this code is in compliance with the [code license](LICENSE).