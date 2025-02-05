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

Per default niicat is using `imgcat` from iterm2. If this is causing problems or you are not using iterm2 you can also try using niicat with the option `-ls` to use libsixel-python or with the option `-lb` (this will use `libsixel-bin` which can be installed via `sudo apt install libsixel-bin`).

Niicat was only tested on python >= 3.7.


### Copyright

Copyright © German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC).
Please make sure that your usage of this code is in compliance with the [code license](LICENSE).
