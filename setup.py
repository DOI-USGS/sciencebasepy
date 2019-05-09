import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='sciencebasepy',
      version='1.6.4',
      author="USGS ScienceBase Development Team",
      author_email="sciencebase@usgs.gov",
      description="Python ScienceBase Utilities",
      long_description=long_description,
      url='https://github.com/usgs/sciencebasepy',
      packages=setuptools.find_packages(),
      classifiers=[        
        "License :: Public Domain",
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
      ],
      )
