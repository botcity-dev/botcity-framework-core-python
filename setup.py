from setuptools import setup, find_packages
from os import path, environ
import versioneer

cur_dir = path.abspath(path.dirname(__file__))

with open(path.join(cur_dir, 'requirements.txt'), 'r') as f:
    requirements = f.read().split()

setup(
    name='botcity',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    package_dir={'botcity': 'botcity'},
    url='https://www.botcity.dev/',
    long_description=open('README').read(),
    long_description_content_type='text/markdown',
    install_requires=requirements,
    include_package_data=True,
    python_requires='>=3.6'
)