from setuptools import setup, find_packages
setup(
   name = "metafilter",
   version = "0.1",
   packages = find_packages(),
   scripts = ['metafilter/webserve.py', 'metafilter/rescan_folder.py', 'metafilter/metafilterfs.py'],
   install_requires = [
      'parsedatetime',
      'Flask==0.6',
      'sqlalchemy==0.6.5',
      'psycopg2==2.3.0',
      'PIL',
      ],
   author = "Michel Albert",
   author_email = "michel@albert.lu",
   description = "File indexer",
   license = "BSD",
)
