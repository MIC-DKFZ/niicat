# niicat

This is a tool to quickly preview nifti images on the terminal. 
This can be helpful if you are working on a remote server via SSH and do not have
a -X connection. It uses [libsixel](https://github.com/saitoha/libsixel) to display the images.


### Install:

```
pip install niicat
```

Also check out the [terminal requirements](https://github.com/saitoha/libsixel#terminal-requirements) for 
libsixel to work.


### Usage:

```
niicat T1.nii.gz
```

![](niicat/resources/example.gif)


### This code is based on the following code:

[niipre](https://github.com/vnckppl/niipre)  
