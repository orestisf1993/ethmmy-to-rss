from setuptools import setup, find_packages

setup(name='ethmmy-to-rss', version='0.1', packages=find_packages(),
      url='https://github.com/orestisf1993/ethmmy-to-rss', license='', author='orestis', author_email='',
      description='A script to convert announcements from eTHMMY to rss feeds',
      install_requires=['requests', 'keyring', 'beautifulsoup4', 'jinja2'],
      extras_require={'Gnome Keyring support': 'SecretStorage'}, package_data={'ethmmyrss': ['feed-template.xml']},
      entry_points={
          'console_scripts': ['ethmmy-rss = ethmmyrss.main:main']
      })
