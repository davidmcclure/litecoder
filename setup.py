

from setuptools import setup, find_packages


PACKAGE_DATA = {
    'litecoder': [
        'data/*.db',
        'data/*.yml',
        'data/*.p',
    ]
}

INSTALL_REQUIRES = [
    'numpy',
    'scipy',
    'SQLAlchemy',
    'us',
    'boltons',
    'cached-property',
    'tqdm',
    'attrs',
    'ujson',
    'python-box',
    'PyYAML',
]

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
]


setup(
    name='litecoder',
    version='0.1.1',
    description='US city + state geocoding.',
    url='https://github.com/davidmcclure/litecoder',
    license='MIT',
    author='David McClure',
    author_email='dclure@mit.edu',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    package_data=PACKAGE_DATA,
)
