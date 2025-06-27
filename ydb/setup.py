from setuptools import setup
setup(
    name='mdb',
    version='1.0.1',
    packages = ['ydb'],
    entry_points='''
        [console_scripts]
        mdb=ydb.ydb:main
    ''',
)

