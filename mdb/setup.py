from setuptools import setup
setup(
    name='mdb',
    version='1.0.1',
    packages = ['mdb'],
    entry_points='''
        [console_scripts]
        mdb=mdb.mdb:main
    ''',
)

