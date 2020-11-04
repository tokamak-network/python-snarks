from setuptools import (
    find_packages,
    setup
)

extras_require = {
    'dev': [
        'bumpversion'
    ]
}

with open('./README.md') as readme:
    long_description = readme.read()

setup(
    name='python-snarks',
    version='0.0.1',
    description="""python_snarks""",
    long_description_content_type='text/markdown',
    long_description=long_description,
    author='Onther Inc.',
    author_email='info@onther.io',
    url='https://github.com/Onther-Tech/python-snarks',
    include_package_data=True,
    install_requires=[
        'fnv>=0.2.0',
        'wasmer>=1.0.0a3',
        'wasmer_compiler_cranelift>=1.0.0a3',
        'pytest>=6.1.2'
    ],
    python_requires='>=3.6,<4',
    extras_require=extras_require,
    py_modules=['python_snarks'],
    license='GPLv3',
    zip_safe=False,
    keywords='snarks',
    packages=find_packages(exclude=['tests']),
    #packages=['python_snarks'],
    package_data={'python_snarks': ['py.typed']},
    #package_dir={'': 'python_snarks'},
    #package_dir={'python_snarks': '',},
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
)
