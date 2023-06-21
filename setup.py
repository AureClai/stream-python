import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stream",
    version="3.2.2",
    author="CEREMA",
    author_email="aurelien.clairais@cerema.fr",
    description="A mesoscopic event-base open-source traffic simulation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AureClai/stream-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Cecill-B",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'pyqt6'
    ],
    py_modules=['stream','stream_gui'],
    entry_points={
        'console_scripts': [
            'stream-gui = stream_gui:main',
            'stream = stream:main',
        ]
    }
)
