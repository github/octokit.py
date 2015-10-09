#!/usr/bin/env python3

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


version = '0.1'
authors = ''
emails = ''
package = []
requires = [
  "requests >= 2.8.0",
  "uritemplate >= 0.5",
  "inflection >= 0.3.1"
]

setup(
  name='octokit',
  version=version,
  description='Simple wrapper for the GitHub API',
  long_description="Python toolkit for working with the GitHub API",
  author=authors,
  author_email=emails,
  url='https://github.com/octokit/octokit.py',
  packages=package,
  install_requires=requires,
  license='MIT',
)
