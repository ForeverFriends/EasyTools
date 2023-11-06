from setuptools import setup
setup(
    name='megaqdb',
    version='1.1',
    packages = ['megaqdb'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        qdb=megaqdb.qdb:main
    ''',
)

