from distutils.core import setup
setup(name='sciencebasepy',
      version='1.6.1',
      packages=['sciencebasepy',],
      description="Python ScienceBase Utilities",
      author="ScienceBase Development Team",
      author_email="sciencebase@usgs.gov",
      url='https://my.usgs.gov/confluence/display/sciencebase/ScienceBase+Item+Services',
      install_requires=[
        'requests'
      ]
      )
