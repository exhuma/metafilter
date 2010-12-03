from setuptools import setup, find_packages
setup(
   name = "metafilter",
   version = "0.1",
   packages = find_packages(),
   scripts = ['webserve.py', 'rescan_folder.py', 'metafilterfs.py'],
   install_requires = [
      'Flask==0.6',
      'sqlalchemy==0.6.5',
      'psycopg2==2.3.0',
      'fuse-python',
      ],
   author = "Michel Albert",
   author_email = "michel@albert.lu",
   description = "File indexer",
   license = "BSD",
)
