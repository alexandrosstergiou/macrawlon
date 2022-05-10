from setuptools import setup

with open("README.md", "r") as fh:

    long_description = fh.read()

setup(name='macrawlon',
      version='0.1',
      description='A sweet little collection of handy functions for video file downloading. 📼',
      url='https://github.com/alexandrosstergiou/macrawlon',
      author='Alexandros Stergiou',
      author_email='alexstergiou5@gmail.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='MIT',
      packages=['macrawlon'],
      install_requires=[
          'pandas',
          'youtube-dl',
          'pafy',
          'tqdm'],
      zip_safe=False)
