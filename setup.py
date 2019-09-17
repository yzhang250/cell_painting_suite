import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    include_package_data=True,
    package_data={
            # If any package contains *.txt or *.rst files, include them:
            'cpimgs': ['metadata*', 'CPD*'],
        },
    name="cpimgs-yzhang250",
    version="0.1.3",
    author="Ye Zhang",
    author_email="yzhang250@gmail.com",
    description="A package to get DMSO plates and wells coordinates, get CPD plates and wells coordinates, get images of " +
                "the cells treated by the CPD and nearby DMSO.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yzhang250",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)