from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['jsonschema[format_nongpl]==3.2.0', 'pyyaml>=5.4.1', 'requests>=2.18']

setup(
    name='alertlogic-sdk-definitions',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    url='https://github.com/alertlogic/alertlogic-sdk-definitions',
    license='MIT license',
    author='Alert Logic Inc.',
    author_email='devsupport@alertlogic.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    description='The Alert Logic API definitions.',
    long_description=readme,
    long_description_content_type='text/markdown',
    scripts=[],
    # yeah yeah i know, circular dependency, but we need it for test now, later i'll think how to decouple
    # definitions parsing/loading and client
    tests_require=requirements,
    packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'troubleshooting']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=3',
            'mock>=2.0.0',
            'httpretty>=0.8.14',
            'pycodestyle>=2.3.1'
        ],
    },
    keywords=['alcli', 'almdr', 'alsdkdefs', 'alertlogic', 'alertlogic-cli']
)
