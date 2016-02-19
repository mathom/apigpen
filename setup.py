from setuptools import setup
import os
import re

# snippet from github.com/miserlou/zappa
try:
    from pypandoc import convert
    README = convert('README.md', 'rst')
except ImportError:
    README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    REQUIRED = f.read().splitlines()


# the following is from airbrake-python to grab the version
_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('apigpen/__init__.py', 'rb') as f:
    text = f.read()
    VERSION = str(ast.literal_eval(_version_re.search(
        text.decode('utf-8')).group(1)))


SCRIPTS = [
    os.path.join(os.path.dirname(__file__), 'bin', 'apigpen')
]


setup(
    name='apigpen',
    version=VERSION,
    author='Matthew Thompson',
    author_email='chameleonator@gmail.com',
    packages=['apigpen'],
    scripts=SCRIPTS,
    url='https://github.com/mathom/apigpen',
    license='MIT License',
    description='Import and export Amazon API Gateway projects.',
    long_description=README,
    install_requires=REQUIRED,
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
