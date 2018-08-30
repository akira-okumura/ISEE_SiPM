from distutils.core import setup

description = '''Common Python toolset for SiPM analysis'''

setup(name='ISEE_SiPM',
      version='1.1.0',
      description='Commont Python toolset for SiPM analysis',
      author='Akira Okumura',
      author_email='oxon@mac.com',
      license='MIT License',
      platforms=['MacOS :: MacOS X', 'POSIX', 'Windows'],
      url='https://github.com/akira-okumura/ISEE_SiPM',
      py_modules=['isee_sipm'],
      install_requires=['numpy'],
      classifiers=['Topic :: Terminals :: Serial',
                   'Development Status :: 5 - Production/Stable',
                   'Programming Language :: Python',
                   ],
      long_description=description
      )
