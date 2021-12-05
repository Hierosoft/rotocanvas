import setuptools
import sys
# - For the example on which this was based, see
#   https://github.com/poikilos/nopackage/blob/master/setup.py
#   which was based on:
#   - https://github.com/poikilos/pypicolcd/blob/master/setup.py
#   - (For nose) https://github.com/poikilos/mgep/blob/master/setup.py

python_mr = sys.version_info.major
versionedModule = {}
versionedModule['urllib'] = 'urllib'
if python_mr == 2:
    versionedModule['urllib'] = 'urllib2'
long_description = ""
with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='rotocanvas',
    version='0.3.0',
    description=("Automate the installation of any source with zero"
                 " configuration. The source can be a zip or gz binary"
                 " package, appimage, directory, or executable file."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        ('License :: OSI Approved ::'
         ' GNU General Public License v3 or later (GPLv3+)'),
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Installation/Setup',
    ],
    keywords='python batch image processing video editing manipulation gimp plugins imgdiff imagediff compare images channeltinker channeltinkerpil channeltinkergimp',
    url="https://github.com/poikilos/rotocanvas",
    author="Jake Gustafson",
    author_email='7557867+poikilos@users.noreply.github.com',
    license='GPLv3+',
    # packages=setuptools.find_packages(),
    packages=['rotocanvas', 'channeltinker', 'channeltinkerpil'],
    include_package_data=True,  # look for MANIFEST.in
    # scripts=['example'] ,
    # See <https://stackoverflow.com/questions/27784271/
    # how-can-i-use-setuptools-to-generate-a-console-scripts-entry-
    # point-which-calls>
    entry_points={
        'console_scripts': [
            'diffimage=channeltinkerpil.diffimage:main',
            'diffimagesratio=channeltinkerpil.diffimagesratio:main',
            'findbyappearance=channeltinkerpil.findbyappearance:main',
        ],
    },
    install_requires=[
        'Pillow',
    ],
    #     versionedModule['urllib'],
    # ^ "ERROR: Could not find a version that satisfies the requirement urllib (from nopackage) (from versions: none)
    # ERROR: No matching distribution found for urllib"
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3'],
    zip_safe=False, # It can't run zipped due to needing data files.
 )
