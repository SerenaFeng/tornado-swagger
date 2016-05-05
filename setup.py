try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README') as file:
    long_description = file.read()

setup(name='tornado-swagger',
      version='1.0',
      url='https://github.com/SerenaFeng/tornado-swagger',
      zip_safe=False,
      packages=['tornado_swagger'],
      package_data={
        'tornado_swagger': [
          'static/*.*',
          'static/css/*.*',
          'static/images/*.*',
          'static/lib/*.*',
          'static/lib/shred/*.*',
        ]
      },
      description='Extract swagger specs from your tornado project',
      author='Serena Feng',
      license='MIT',
      long_description=long_description,
      install_requires=[
        'tornado>=3.1',
        'epydoc>=0.3.1'
      ],
)
