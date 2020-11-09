import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ign-rocker",
    version="0.0.1",
    packages=setuptools.find_packages(),
    package_data={'ign_rocker': ['templates/*.em']},
    author="Ashton Larkin",
    author_email="42042756+adlarkin@users.noreply.github.com",
    description="Plugins for rocker that enable the use of Ignition Robotics libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adlarkin/ign-rocker",
    license='Apache 2.0',
    install_requires=[
        'rocker',
    ],
    entry_points={
        'rocker.extensions': [
            'ignition = ign_rocker.ignition:Ignition',
            'vol = ign_rocker.vol:Vol',
        ]
    }
)
