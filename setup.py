from setuptools import find_packages, setup

version = open('Ctl/VERSION').read().strip()
requirements = open('Ctl/requirements.txt').read().split("\n")
test_requirements = open('Ctl/requirements-test.txt').read().split("\n")


setup(
    name='vodka',
    version=version,
    author='Twentieth Century',
    author_email='code@20c.com',
    description='vodka is a plugin based real-time web service daemon',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
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
