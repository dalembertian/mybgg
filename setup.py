import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='mybgg',
    version='0.1',
    scripts=['mybgg'] ,
    author="Rubens Altimari",
    author_email="rubens@altimari.nl",
    description="A command-line tool to query someone's game collection at boardgamegeek.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dalembertian/mybgg",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
     ],
    install_requires=[
        'boardgamegeek2',
    ]
    # python_requires='>=3.6',
 )