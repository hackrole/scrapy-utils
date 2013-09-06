
#!/usr/bin/python
#coding=utf-8
sys.path.append('./src')
from distutils.core import setup
from recrawler import __version__
setup(name='recrawler',
      version=__version__,
      description='A python empty project',
      long_description=open('README.md').read(),
      author='solos',
      author_email='solos@solos.so',
      packages=['recrawler'],
      package_dir={'recrawler': 'src/recrawler'},
      package_data={'recrawler': ['stuff']},
      license='BSD',
      platforms=['any'],
      url='https://github.com/solos/recrawler')
