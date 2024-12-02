# to install the requirements

from setuptools import find_packages,setup

setup(
    name='marketing_assistant',
    version='0.0.1',
    author='faiz hadiyan',
    author_email='faizhadiyanfirza@gmail.com',
    install_requires=[
        "openai",
        "langchain",
        "langchain-community",
        "langchain-openai",
        "streamlit",
        "python-dotenv",
        "PyPDF2",
        "pandas",
        "numpy"
    ],
    packages=find_packages()
)