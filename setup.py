from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()

setup(
    name="djangorestframework-more",
    packages=["rest_framework_more"],
    package_dir={"rest_framework_more": "rest_framework_more"},
    package_data={
        "rest_framework_more": [
            "__init__.py",
            "filters.py",
            "mixins.py",
            "renderers.py",
            "serializers.py",
            "viewsets.py",
        ]
    },
    version="1.2.0",
    description="More Cool Django Rest Framework Stuff",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daniel J. Dufour",
    author_email="daniel.j.dufour@gmail.com",
    url="https://github.com/DanielJDufour/djangorestframework-more",
    download_url="https://github.com/DanielJDufour/djangorestframework-more/tarball/download",
    keywords=[
        "csv",
        "django",
        "django-rest-framework",
        "drf",
        "djangorestframework-csv",
        "excel",
        "pagination",
        "xlsx",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "djangorestframework-csv",
        "drf-renderer-xlsx",
        "prune",
        "simple-env",
    ],
)
