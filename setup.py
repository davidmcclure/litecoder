

from setuptools import setup, find_packages


setup(
    name='litecoder',
    version='0.1.0',
    description='Simple geocoding.',
    url='https://github.com/davidmcclure/litecoder',
    license='MIT',
    author='David McClure',
    author_email='dclure@mit.edu',
    packages=find_packages(),
    include_package_data=True,
    package_data={'litecoder': ['litecoder.db']},
    install_requires=[
        'sqlalchemy',
        'us',
        'boltons',
        'invoke',
        'cached-property',
        'tqdm',
        'wordfreq',
        'pandas',
        'attrs',
        'pytest',
    ],
)
