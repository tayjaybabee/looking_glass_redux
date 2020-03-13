from setuptools import setup

setup(name='looking_glass',
      version='2.0',
      description='Look at your climate',
      url='http://github.com/tayjaybabee/looking_glass',
      author='Taylor-Jayde',
      author_email='t.blackstone@inspyre.tech',
      license='MIT',
      packages=['looking_glass'],
      zip_safe=False,
      install_requires=[
          'markdown',
      ],
      include_package_data = True,
      scripts=['bin/looking-glass']
      )
