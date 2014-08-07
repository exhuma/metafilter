from setuptools import setup, find_packages

setup(
    name="metafilter",
    version="0.1",
    packages=find_packages(),
    scripts=[
        'metafilter/webserve.py',
        'metafilter/rescan_query.py',
        'metafilter/rescan_folder.py',
        'metafilter/metafilterfs.py'
    ],
    install_requires=[
        'Flask==0.6',
        'PIL',
        'config_resolver<4.0',
        'fusepy==2.0.2',
        'parsedatetime',
        'parsedatetime==1.1.2',
        'psycopg2==2.3.0',
        'simplejson',
        'sqlalchemy==0.6.5',
    ],
    author="Michel Albert",
    author_email="michel@albert.lu",
    description="File indexer",
    license="BSD",
)
