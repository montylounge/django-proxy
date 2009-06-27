from setuptools import setup, find_packages
 
setup(
    name='django-proxy',
    version='0.1.0',
    description='This is a content aggregation solution via proxy intermediary models.',
    author='Kevin Fricovsky',
    author_email='kfricovsky@gmail.com',
    url='http://bitbucket.org/montylounge/django-proxy/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
)
 
