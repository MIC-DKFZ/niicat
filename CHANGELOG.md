## Release 0.6.0
* speed up png/jpeg display by sending the original file to imgcat/img2sixel instead of re-rendering with matplotlib
* speed up nifti previews with a lightweight Pillow-based renderer (matplotlib still used for `-ls`)
* add Pillow dependency
* add `-kt` option for Kitty graphics protocol
* use the current Python interpreter / subprocess instead of shelling out to a bare `python` (fixes pipx/venv setups)

## Release 0.5.0
* support rgb dtypes
* change default dpi to 200
* make iTerm2's imgcat the default (instead of libsixel-python which does not work so well)

## Release 0.4.4
* udpate plotter for nibabel 5.0


