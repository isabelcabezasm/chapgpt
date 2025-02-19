from setuptools import setup, find_packages

setup(
    name='caps_common',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'azure-identity',
        'pandas',
        'python-dotenv',
        # Add other dependencies here
    ],
)