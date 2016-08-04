from setuptools import find_packages, setup

version = open('facsimile/VERSION').read().strip()
requirements = open('facsimile/requirements.txt').read().split("\n")
test_requirements = open('facsimile/requirements-test.txt').read().split("\n")


setup(
    name='vodka',
    version=version,
    author='Twentieth Century',
    author_email='code@20c.com',
    description='vodka is a plugin based real-time web service daemon',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License'
    ],
    packages = find_packages(),
    install_requires=requirements,
    test_requires=test_requirements,
    url='https://github.com/20c/vodka',
    download_url='https://github.com/20c/vodka/%s' % version,
    entry_points={
        'console_scripts': [
            'bartender=vodka.bartender:bartender'
        ]
    },
    include_package_data=True,
    zip_safe=True
)
