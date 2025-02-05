from setuptools import setup, find_packages

with open("Readme.md", "r") as f:
    long_description = f.read()

setup(name='niicat',
      version='0.4.4',
      description='Preview nifti images on the terminal',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/MIC-DKFZ/niicat/',
      author='Jakob Wasserthal',
      author_email='j.wasserthal@dkfz.de',
      python_requires='>=3.7',
      license='GPL v2',
      packages=find_packages(),
      install_requires=[
          'nibabel>=2.3.0',
          'matplotlib',
          'numpy',
          'importlib-metadata;python_version<"3.8"'
      ],
      extras_require={
          'libsixel': ['libsixel-python'],
      },
      zip_safe=False,
      classifiers=[
          'Intended Audience :: Science/Research',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Operating System :: Unix',
          'Operating System :: MacOS'
      ],
      entry_points={
          'console_scripts': [
              'niicat=niicat.cli:main',
          ],
      },
      package_data={'niicat.resources': ['imgcat.sh', 'niipre.py']},
)
