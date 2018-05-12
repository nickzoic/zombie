from setuptools import setup

setup(
  name='zombie',
  version='0.0.1',
  description='ZOMBIE: Remote control of the DOM',
  url='http://github.com/nickzoic/zombie/',
  author='Nick Moore',
  author_email='nick@zoic.org',
  license="MIT",
  packages=["zombie"],
  install_requires=[
  ],
  extras_require = {
      'bottle': [ "bottle>=0.12.3"],
      'django': [ "django>=2.0.5"],
  },
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3 :: Only',
  ],
)
