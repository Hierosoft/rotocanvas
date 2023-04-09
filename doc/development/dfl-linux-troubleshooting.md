# DeepFaceLabs From Source - Troubleshooting
(unofficial)

These steps were used to improve the "Installing from git section" of the
DeepFaceLabs on Linux document, . The
[System Requirements Troubleshooting](#) section includes steps taken
to improve the System Requirements section.

All of the info below should be already integrated into the [Installing from git](dfl-linux.md#installing-from-git) section of the main document.


## Python Requirements Troubleshooting

opencv line (4.1.0.25 doesn't exist for linux on pip):
```patch
-opencv-python==4.1.0.25
+opencv-python==4.3.0.38
```

- Fixes `ERROR: Could not find a version that satisfies the requirement opencv-python==4.1.0.25 (from versions: 3.4.0.14, 3.4.10.37, 3.4.11.39, 3.4.11.41, 3.4.11.43, 3.4.11.45, 3.4.13.47, 3.4.15.55, 3.4.16.57, 3.4.16.59, 3.4.17.61, 3.4.17.63, 3.4.18.65, 4.3.0.38, 4.4.0.40, 4.4.0.42, 4.4.0.44, 4.4.0.46, 4.5.1.48, 4.5.3.56, 4.5.4.58, 4.5.4.60, 4.5.5.62, 4.5.5.64, 4.6.0.66, 4.7.0.68, 4.7.0.72)
  ERROR: No matching distribution found for opencv-python==4.1.0.25`

```patch
-tensorflow-gpu==2.4.0
+tensorflow-gpu==2.5.3
```

- Fixes `ERROR: Could not find a version that satisfies the requirement tensorflow-gpu==2.4.0 (from versions: 2.5.0, 2.5.1, 2.5.2, 2.5.3, 2.6.0, 2.6.1, 2.6.2, 2.6.3, 2.6.4, 2.6.5, 2.7.0rc0, 2.7.0rc1, 2.7.0, 2.7.1, 2.7.2, 2.7.3, 2.7.4, 2.8.0rc0, 2.8.0rc1, 2.8.0, 2.8.1, 2.8.2, 2.8.3, 2.8.4, 2.9.0rc0, 2.9.0rc1, 2.9.0rc2, 2.9.0, 2.9.1, 2.9.2, 2.9.3, 2.10.0rc0, 2.10.0rc1, 2.10.0rc2, 2.10.0rc3, 2.10.0, 2.10.1, 2.11.0rc0, 2.11.0rc1, 2.11.0rc2, 2.11.0, 2.12.0)
ERROR: No matching distribution found for tensorflow-gpu==2.4.0`
  - There is a precompiled wheel for 2.5.3 for Python 3.9 on linux.

```patch
-h5py==2.10.0
+h5py==3.1.0
```

- Fixes
```
ERROR: Cannot install -r requirements-cuda.txt (line 10) and h5py==2.10.0 because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested h5py==2.10.0
    tensorflow-gpu 2.5.3 depends on h5py~=3.1.0`
```
  - `ERROR: Could not find a version that satisfies the requirement h5py==4.0.0 (from versions: 2.2.1, 2.3.0b1, 2.3.0, 2.3.1, 2.4.0b1, 2.4.0, 2.5.0, 2.6.0, 2.7.0rc2, 2.7.0, 2.7.1, 2.8.0rc1, 2.8.0, 2.9.0rc1, 2.9.0, 2.10.0, 3.0.0rc1, 3.0.0, 3.1.0, 3.2.0, 3.2.1, 3.3.0, 3.4.0, 3.5.0, 3.6.0, 3.7.0, 3.8.0)
ERROR: No matching distribution found for h5py==4.0.0`


```
Building wheel for opencv-python (pyproject.toml) ... error
  error: subprocess-exited-with-error

  × Building wheel for opencv-python (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [1411 lines of output]
```

tried:
- `sudo ldconfig`

opencv build still has many errors like:
```
      Error: Rank mismatch between actual argument at (1) and actual argument at (2) (scalar and rank-1)
      gfortran:f77: scipy/sparse/linalg/eigen/arpack/ARPACK/SRC/dstatn.f
      gfortran:f77: scipy/sparse/linalg/eigen/arpack/ARPACK/SRC/dneigh.f
      stat.h:8:19:

      Warning: Unused variable ‘t0’ declared at (1) [-Wunused-variable]
      stat.h:8:23:

      Warning: Unused variable ‘t1’ declared at (1) [-Wunused-variable]
      stat.h:8:27:
```

- <https://bugs.gentoo.org/721860> says "SOLVED" via a Gentoo package change, but also:
```
+	# Remove once upstream PR #11842 lands into next release
+	append-fflags -fallow-argument-mismatch
```
- related to issue in scipi-1.4.1

So try `from versions: 0.8.0, 0.9.0, 0.10.0, 0.10.1, 0.11.0, 0.12.0, 0.12.1, 0.13.0, 0.13.1, 0.13.2, 0.13.3, 0.14.0, 0.14.1, 0.15.0, 0.15.1, 0.16.0, 0.16.1, 0.17.0, 0.17.1, 0.18.0, 0.18.1, 0.19.0, 0.19.1, 1.0.0, 1.0.1, 1.1.0, 1.2.0, 1.2.1, 1.2.2, 1.2.3, 1.3.0, 1.3.1, 1.3.2, 1.3.3, 1.4.0, 1.4.1, 1.5.0, 1.5.1, 1.5.2, 1.5.3, 1.5.4, 1.6.0, 1.6.1, 1.6.2, 1.6.3, 1.7.0rc1, 1.7.0rc2, 1.7.0, 1.7.1, 1.7.2, 1.7.3, 1.8.0rc1, 1.8.0rc2, 1.8.0rc3, 1.8.0rc4, 1.8.0, 1.8.1, 1.9.0rc1, 1.9.0rc2, 1.9.0rc3, 1.9.0, 1.9.1, 1.9.2, 1.9.3, 1.10.0rc1, 1.10.0rc2, 1.10.0, 1.10.1)`:
```patch
-scipy==1.4.1
+scipy==1.5.0
```

still has:
```
     -- Found PythonInterp: /home/owner/.virtualenvs/deepfacelab/bin/python3.9 (found suitable version "3.9.16", minimum required is "2.7")
      CMake Warning at cmake/OpenCVDetectPython.cmake:81 (message):
        CMake's 'find_host_package(PythonInterp 2.7)' found wrong Python version:

        PYTHON_EXECUTABLE=/home/owner/.virtualenvs/deepfacelab/bin/python3.9

        PYTHON_VERSION_STRING=3.9.16

        Consider providing the 'PYTHON2_EXECUTABLE' variable via CMake command line
        or environment variables

      Call Stack (most recent call first):
        cmake/OpenCVDetectPython.cmake:271 (find_python)
        CMakeLists.txt:598 (include)


      -- Found Python2: /usr/bin/python2.7 (found version "2.7.18") found components: Interpreter
      -- Found PythonInterp: /usr/bin/python2.7 (found version "2.7.18")
      -- Could NOT find PythonLibs: Found unsuitable version "3.9.16", but required is exact version "2.7.18" (found /usr/lib64/libpython3.9.so)
      Error processing line 1 of /home/owner/.virtualenvs/deepfacelab/lib/python3.9/site-packages/distutils-precedence.pth:

        Traceback (most recent call last):
          File "/usr/lib64/python2.7/site.py", line 152, in addpackage
            exec line
          File "<string>", line 1, in <module>
          File "/home/owner/.virtualenvs/deepfacelab/lib/python3.9/site-packages/_distutils_hack/__init__.py", line 194
            f'spec_for_{name}',
                             ^
        SyntaxError: invalid syntax

      Remainder of file ignored
      Error processing line 1 of /home/owner/.virtualenvs/deepfacelab/lib64/python3.9/site-packages/distutils-precedence.pth:

        Traceback (most recent call last):
          File "/usr/lib64/python2.7/site.py", line 152, in addpackage
            exec line
          File "<string>", line 1, in <module>
        AttributeError: 'module' object has no attribute 'add_shim'

      Remainder of file ignored
      Error processing line 1 of /tmp/pip-build-env-t86u_3zt/overlay/lib/python3.9/site-packages/distutils-precedence.pth:

        Traceback (most recent call last):
          File "/usr/lib64/python2.7/site.py", line 152, in addpackage
            exec line
          File "<string>", line 1, in <module>
        AttributeError: 'module' object has no attribute 'add_shim'

      Remainder of file ignored
      Error processing line 1 of /home/owner/.virtualenvs/deepfacelab/lib/python3.9/site-packages/distutils-precedence.pth:

        Traceback (most recent call last):
          File "/usr/lib64/python2.7/site.py", line 152, in addpackage
            exec line
          File "<string>", line 1, in <module>
          File "/home/owner/.virtualenvs/deepfacelab/lib/python3.9/site-packages/_distutils_hack/__init__.py", line 194
            f'spec_for_{name}',
                             ^
        SyntaxError: invalid syntax

      Remainder of file ignored
      Error processing line 1 of /home/owner/.virtualenvs/deepfacelab/lib64/python3.9/site-packages/distutils-precedence.pth:

        Traceback (most recent call last):
          File "/usr/lib64/python2.7/site.py", line 152, in addpackage
            exec line
          File "<string>", line 1, in <module>
        AttributeError: 'module' object has no attribute 'add_shim'

      Remainder of file ignored
      Error processing line 1 of /tmp/pip-build-env-t86u_3zt/overlay/lib/python3.9/site-packages/distutils-precedence.pth:

        Traceback (most recent call last):
          File "/usr/lib64/python2.7/site.py", line 152, in addpackage
            exec line
          File "<string>", line 1, in <module>
        AttributeError: 'module' object has no attribute 'add_shim'

      Remainder of file ignored
      Traceback (most recent call last):
        File "<string>", line 1, in <module>
        File "/tmp/pip-build-env-t86u_3zt/overlay/lib64/python3.9/site-packages/numpy/__init__.py", line 142, in <module>
          from . import core
        File "/tmp/pip-build-env-t86u_3zt/overlay/lib64/python3.9/site-packages/numpy/core/__init__.py", line 47, in <module>
          raise ImportError(msg)
      ImportError:

      IMPORTANT: PLEASE READ THIS FOR ADVICE ON HOW TO SOLVE THIS ISSUE!

      Importing the numpy c-extensions failed.
      - Try uninstalling and reinstalling numpy.
      - If you have already done that, then:
        1. Check that you expected to use Python2.7 from "/usr/bin/python2.7",
           and that you have no directories in your PATH or PYTHONPATH that can
           interfere with the Python and numpy version "1.17.3" you're trying to use.
        2. If (1) looks fine, you can open a new issue at
           https://github.com/numpy/numpy/issues.  Please include details on:
           - how you installed Python
           - how you installed numpy
           - your operating system
           - whether or not you have multiple versions of Python installed
           - if you built from source, your compiler versions and ideally a build log

      - If you're working with a numpy git repository, try `git clean -xdf`
        (removes all files not under version control) and rebuild numpy.

      Note: this error has many possible causes, so please don't comment on
      an existing issue about this - open a new one instead.

      Original error was: No module named _multiarray_umath

      . . .
      -- Looking for ccache - not found
      . . .
      -- Could NOT find JNI (missing: JAVA_INCLUDE_PATH JAVA_INCLUDE_PATH2 AWT)
      -- VTK is not found. Please set -DVTK_DIR in CMake to VTK build directory, or to VTK install subdirectory with VTKConfig.cmake file
      -- Performing Test HAVE_C_WNO_UNUSED_VARIABLE
      -- Performing Test HAVE_C_WNO_UNUSED_VARIABLE - Success
      -- Looking for dlerror in dl
      -- Looking for dlerror in dl - found
      -- Performing Test HAVE_C_WNO_UNDEF
      -- Performing Test HAVE_C_WNO_UNDEF - Success
      -- ADE: Download: v0.1.1f.zip
      -- Checking for modules 'libavcodec;libavformat;libavutil;libswscale'
      --   Package 'libavcodec', required by 'virtual:world', not found
      --   Package 'libavformat', required by 'virtual:world', not found
      --   Package 'libavutil', required by 'virtual:world', not found
      --   Package 'libswscale', required by 'virtual:world', not found
      -- Checking for module 'gstreamer-base-1.0'
      --   Found gstreamer-base-1.0, version 1.20.5
      -- Checking for module 'gstreamer-app-1.0'
      --   Package 'gstreamer-app-1.0', required by 'virtual:world', not found
      -- Checking for module 'gstreamer-riff-1.0'
      --   Package 'gstreamer-riff-1.0', required by 'virtual:world', not found
      -- Checking for module 'gstreamer-pbutils-1.0'
      --   Package 'gstreamer-pbutils-1.0', required by 'virtual:world', not found
      -- Checking for module 'libdc1394-2'
      --   Package 'libdc1394-2', required by 'virtual:world', not found

      . . .
  Building wheel for scikit-image (pyproject.toml) ... error
  error: subprocess-exited-with-error

  × Building wheel for scikit-image (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [865 lines of output]
      <string>:78: DeprecationWarning:

        `numpy.distutils` is deprecated since NumPy 1.23.0, as a result
        of the deprecation of `distutils` itself. It will be removed for
        Python >= 3.12. For older Python versions it will remain present.
        It is recommended to use `setuptools < 60.0` for those Python versions.
        For more details, see:
          https://numpy.org/devdocs/reference/distutils_status_migration.html

```



still has
```
     -- Found PythonInterp: /home/owner/.virtualenvs/deepfacelab/bin/python3.9 (found suitable version "3.9.16", minimum required is "2.7")
      CMake Warning at cmake/OpenCVDetectPython.cmake:81 (message):
        CMake's 'find_host_package(PythonInterp 2.7)' found wrong Python version:

        PYTHON_EXECUTABLE=/home/owner/.virtualenvs/deepfacelab/bin/python3.9

        PYTHON_VERSION_STRING=3.9.16

        Consider providing the 'PYTHON2_EXECUTABLE' variable via CMake command line
        or environment variables

      Call Stack (most recent call first):
        cmake/OpenCVDetectPython.cmake:271 (find_python)
        CMakeLists.txt:598 (include)


      -- Found Python2: /usr/bin/python2.7 (found version "2.7.18") found components: Interpreter
      -- Found PythonInterp: /usr/bin/python2.7 (found version "2.7.18")
      -- Could NOT find PythonLibs: Found unsuitable version "3.9.16", but required is exact version "2.7.18" (found /usr/lib64/libpython3.9.so)
      Error processing line 1 of /home/owner/.virtualenvs/deepfacelab/lib64/python3.9/site-packages/distutils-precedence.pth:

        Traceback (most recent call last):
          File "/usr/lib64/python2.7/site.py", line 152, in addpackage
            exec line
          File "<string>", line 1, in <module>
          File "/home/owner/.virtualenvs/deepfacelab/lib64/python3.9/site-packages/_distutils_hack/__init__.py", line 194
            f'spec_for_{name}',
                             ^
        SyntaxError: invalid syntax

      Remainder of file ignored
      Error processing line 1 of /home/owner/.virtualenvs/deepfacelab/lib/python3.9/site-packages/distutils-precedence.pth:

        Traceback (most recent call last):
          File "/usr/lib64/python2.7/site.py", line 152, in addpackage
            exec line
          File "<string>", line 1, in <module>
        AttributeError: 'module' object has no attribute 'add_shim'

      Remainder of file ignored

      . . .

        AttributeError: 'module' object has no attribute 'add_shim'

      Remainder of file ignored
      Error processing line 1 of /tmp/pip-build-env-fyof3piq/overlay/lib/python3.9/site-packages/distutils-precedence.pth:

        Traceback (most recent call last):
          File "/usr/lib64/python2.7/site.py", line 152, in addpackage
            exec line
          File "<string>", line 1, in <module>
        AttributeError: 'module' object has no attribute 'add_shim'

      Remainder of file ignored
      Traceback (most recent call last):
        File "<string>", line 1, in <module>
        File "/tmp/pip-build-env-fyof3piq/overlay/lib64/python3.9/site-packages/numpy/__init__.py", line 142, in <module>
          from . import core
        File "/tmp/pip-build-env-fyof3piq/overlay/lib64/python3.9/site-packages/numpy/core/__init__.py", line 47, in <module>
          raise ImportError(msg)
      ImportError:

      IMPORTANT: PLEASE READ THIS FOR ADVICE ON HOW TO SOLVE THIS ISSUE!

      Importing the numpy c-extensions failed.
      - Try uninstalling and reinstalling numpy.
      - If you have already done that, then:
        1. Check that you expected to use Python2.7 from "/usr/bin/python2.7",
           and that you have no directories in your PATH or PYTHONPATH that can
           interfere with the Python and numpy version "1.17.3" you're trying to use.
        2. If (1) looks fine, you can open a new issue at
           https://github.com/numpy/numpy/issues.  Please include details on:
           - how you installed Python
           - how you installed numpy
           - your operating system
           - whether or not you have multiple versions of Python installed
           - if you built from source, your compiler versions and ideally a build log

      - If you're working with a numpy git repository, try `git clean -xdf`
        (removes all files not under version control) and rebuild numpy.

      Note: this error has many possible causes, so please don't comment on
      an existing issue about this - open a new one instead.

      Original error was: No module named _multiarray_umath

      . . .

      512pf -Werror) failed with exit status 1 output ->
      In file included from /usr/lib/gcc/x86_64-redhat-linux/12/include/immintrin.h:51,
                       from /tmp/pip-build-env-_0hf2su1/overlay/lib64/python3.9/site-packages/numpy/distutils/checks/cpu_avx512_knl.c:14:
      In function ‘_mm512_exp2a23_round_pd’,
          inlined from ‘main’ at /tmp/pip-build-env-_0hf2su1/overlay/lib64/python3.9/site-packages/numpy/distutils/checks/cpu_avx512_knl.c:21:17:
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h:55:20: error: ‘__W’ is used uninitialized [-Werror=uninitialized]
         55 |   return (__m512d) __builtin_ia32_exp2pd_mask ((__v8df) __A,
            |                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
         56 |                                                (__v8df) __W,
            |                                                ~~~~~~~~~~~~~
         57 |                                                (__mmask8) -1, __R);
            |                                                ~~~~~~~~~~~~~~~~~~~
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h: In function ‘main’:
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h:54:11: note: ‘__W’ was declared here
         54 |   __m512d __W;
            |           ^~~
      In file included from /usr/lib/gcc/x86_64-redhat-linux/12/include/immintrin.h:53:
      In function ‘_mm512_mask_prefetch_i64scatter_pd’,
          inlined from ‘main’ at /tmp/pip-build-env-_0hf2su1/overlay/lib64/python3.9/site-packages/numpy/distutils/checks/cpu_avx512_knl.c:23:5:
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512pfintrin.h:180:3: error: ‘base’ may be used uninitialized [-Werror=maybe-uninitialized]
        180 |   __builtin_ia32_scatterpfqpd (__mask, (__v8di) __index, __addr, __scale,
            |   ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        181 |                                __hint);
            |                                ~~~~~~~
      <built-in>: In function ‘main’:
      <built-in>: note: by argument 3 of type ‘const void *’ to ‘__builtin_ia32_scatterpfqpd’ declared here
      /tmp/pip-build-env-_0hf2su1/overlay/lib64/python3.9/site-packages/numpy/distutils/checks/cpu_avx512_knl.c:18:9: note: ‘base’ declared here
         18 |     int base[128];
            |         ^~~~
      cc1: all warnings being treated as errors

      WARN: CCompilerOpt.feature_test[1567] : testing failed


```
and yet...
"Python 2.7 is not supported anymore in opencv-python-4.3.0.38"
- <https://stackoverflow.com/questions/63346648/python-2-7-installing-opencv-via-pip-virtual-environment>

(


and had

```
      -- Could NOT find OpenJPEG (minimal suitable version: 2.0, recommended version >= 2.3.1)
      -- Could NOT find Jasper (missing: JASPER_LIBRARIES JASPER_INCLUDE_DIR)
VTK is not found. Please set -DVTK_DIR in CMake to VTK build directory, or to VTK install subdirectory with VTKConfig.cmake file
```

- [x] so added these 3 to "install the OS packages" part.
)

(did the "Requirements notes" fixes at this stage, then continued below)

so reinstall numpy as suggested (redo venv).
- tried: PYTHON=python3 (3.10)

```
libraries mkl_rt not found
libraries blis not found
```

<https://numpy.org/doc/stable/user/building.html> says:
> Accelerated BLAS/LAPACK libraries
> NumPy searches for optimized linear algebra libraries such as BLAS and LAPACK. There are specific orders for searching these libraries, as described below and in the site.cfg.example file.
>
> BLAS
> Note that both BLAS and CBLAS interfaces are needed for a properly optimized build of NumPy.
>
> The default order for the libraries are:
> MKL
> BLIS
> OpenBLAS
> ATLAS
> BLAS (NetLIB)

so added openblas-devel and blis-devel to deps (not necessary though it seems, according to the wording.)
- already had openblas-devel

still has:
```
Collecting h5py==3.1.0
  Downloading h5py-3.1.0.tar.gz (371 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 371.4/371.4 kB 6.5 MB/s eta 0:00:00
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Installing backend dependencies ... error
  error: subprocess-exited-with-error

  × pip subprocess to install backend dependencies did not run successfully.
  │ exit code: 1

  . . .
        × Building wheel for numpy (pyproject.toml) did not run successfully.
        │ exit code: 1
        ╰─> [850 lines of output]

        . . .

            In file included from /usr/include/python3.11/bytesobject.h:62,
                             from /usr/include/python3.11/Python.h:50,
                             from numpy/core/src/multiarray/scalarapi.c:2:
            /usr/include/python3.11/cpython/bytesobject.h:7:35: note: declared here
                7 |     Py_DEPRECATED(3.11) Py_hash_t ob_shash;
                  |                                   ^~~~~~~~
            gcc: build/src.linux-x86_64-3.11/numpy/core/src/multiarray/scalartypes.c
            gcc: numpy/core/src/multiarray/temp_elide.c
            numpy/core/src/multiarray/scalartypes.c.src: In function ‘float_arrtype_hash’:
            numpy/core/src/multiarray/scalartypes.c.src:2967:27: error: incompatible type for argument 1 of ‘_Py_HashDouble’
             2967 |     return _Py_HashDouble((double) PyArrayScalar_VAL(obj, @name@));
            In file included from /usr/include/python3.11/Python.h:47,
                             from numpy/core/src/multiarray/scalartypes.c.src:3:
            /usr/include/python3.11/pyhash.h:10:38: note: expected ‘PyObject *’ {aka ‘struct _object *’} but argument is of type ‘double’
               10 | PyAPI_FUNC(Py_hash_t) _Py_HashDouble(PyObject *, double);
                  |                                      ^~~~~~~~~~
            numpy/core/src/multiarray/scalartypes.c.src:2967:12: error: too few arguments to function ‘_Py_HashDouble’
             2967 |     return _Py_HashDouble((double) PyArrayScalar_VAL(obj, @name@));
```

fixed in numpy v1.25.0.dev0:
https://github.com/numpy/numpy/commit/ad2a73c18dcff95d844c382c94ab7f73b5571cf3
- as noted at <https://bugzilla.redhat.com/show_bug.cgi?id=1958052>

uh oh, there is no 0.25.0 yet:
`(from versions: 1.3.0, 1.4.1, 1.5.0, 1.5.1, 1.6.0, 1.6.1, 1.6.2, 1.7.0, 1.7.1, 1.7.2, 1.8.0, 1.8.1, 1.8.2, 1.9.0, 1.9.1, 1.9.2, 1.9.3, 1.10.0.post2, 1.10.1, 1.10.2, 1.10.4, 1.11.0, 1.11.1, 1.11.2, 1.11.3, 1.12.0, 1.12.1, 1.13.0, 1.13.1, 1.13.3, 1.14.0, 1.14.1, 1.14.2, 1.14.3, 1.14.4, 1.14.5, 1.14.6, 1.15.0, 1.15.1, 1.15.2, 1.15.3, 1.15.4, 1.16.0, 1.16.1, 1.16.2, 1.16.3, 1.16.4, 1.16.5, 1.16.6, 1.17.0, 1.17.1, 1.17.2, 1.17.3, 1.17.4, 1.17.5, 1.18.0, 1.18.1, 1.18.2, 1.18.3, 1.18.4, 1.18.5, 1.19.0, 1.19.1, 1.19.2, 1.19.3, 1.19.4, 1.19.5, 1.20.0, 1.20.1, 1.20.2, 1.20.3, 1.21.0, 1.21.1, 1.21.2, 1.21.3, 1.21.4, 1.21.5, 1.21.6, 1.22.0, 1.22.1, 1.22.2, 1.22.3, 1.22.4, 1.23.0rc1, 1.23.0rc2, 1.23.0rc3, 1.23.0, 1.23.1, 1.23.2, 1.23.3, 1.23.4, 1.23.5, 1.24.0rc1, 1.24.0rc2, 1.24.0, 1.24.1, 1.24.2)`
- see further down for version tried...

so try python 3.9 again, but it gives:
```
      Error processing line 1 of /home/owner/.virtualenvs/deepfacelab/lib/python3.9/site-packages/distutils-precedence.pth:

        Traceback (most recent call last):
          File "/usr/lib64/python2.7/site.py", line 152, in addpackage
            exec line
          File "<string>", line 1, in <module>
          File "/home/owner/.virtualenvs/deepfacelab/lib/python3.9/site-packages/_distutils_hack/__init__.py", line 194
            f'spec_for_{name}',
                             ^
        SyntaxError: invalid syntax

      . . .

            -- VTK is not found. Please set -DVTK_DIR in CMake to VTK build directory, or to VTK install subdirectory with VTKConfig.cmake file
```
- See https://bugs.python.org/issue46394

so try:

```patch
-numpy==1.19.3
-numpy==1.21.6
```

which requires bumping everything:
```
The conflict is caused by:
    The user requested numpy==1.21.6
    h5py 3.1.0 depends on numpy>=1.19.3; python_version >= "3.9"
    opencv-python 4.3.0.38 depends on numpy>=1.17.3
    scipy 1.5.0 depends on numpy>=1.14.5
    tensorflow-gpu 2.5.3 depends on numpy~=1.19.2

```

So bumped everything by 1 except h5py to 3.2.1.

Which results in:
```
The conflict is caused by:
    The user requested h5py==3.2.1
    tensorflow-gpu 2.5.3 depends on h5py~=3.1.0

```

so bumped tensorflow-gpu to 2.6.5

resulting in:
```
The conflict is caused by:
    The user requested numpy==1.21.6
    h5py 3.2.1 depends on numpy>=1.19.3; python_version >= "3.9"
    opencv-python 4.4.0.46 depends on numpy>=1.19.3
    scipy 1.6.3 depends on numpy<1.23.0 and >=1.16.5
    tensorflow-gpu 2.6.5 depends on numpy~=1.19.2
```

so try tensorflow-gpu 2.7.4

has:
```
      In function ‘_mm512_exp2a23_round_pd’,
          inlined from ‘main’ at /tmp/pip-build-env-d3kj6dk9/overlay/lib64/python3.9/site-packages/numpy/distutils/checks/cpu_avx512_knl.c:21:17:
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h:55:20: error: ‘__W’ is used uninitialized [-W[redacted]=uninitialized]
         55 |   return (__m512d) __builtin_ia32_exp2pd_mask ((__v8df) __A,
            |                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
         56 |                                                (__v8df) __W,
            |                                                ~~~~~~~~~~~~~
         57 |                                                (__mmask8) -1, __R);
            |                                                ~~~~~~~~~~~~~~~~~~~
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h: In function ‘main’:
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h:54:11: note: ‘__W’ was declared here
         54 |   __m512d __W;
            |           ^~~
      In file included from /usr/lib/gcc/x86_64-redhat-linux/12/include/immintrin.h:53:
      . . .
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512pfintrin.h:180:3: error: ‘base’ may be used uninitialized [-W[redacted]=maybe-uninitialized]
        180 |   __builtin_ia32_scatterpfqpd (__mask, (__v8di) __index, __addr, __scale,
            |   ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        181 |                                __hint);
            |                                ~~~~~~~
      <built-in>: In function ‘main’:
      <built-in>: note: by argument 3 of type ‘const void *’ to ‘__builtin_ia32_scatterpfqpd’ declared here
      . . .
            skimage/_shared/transform.c: In function ‘__Pyx_modinit_type_init_code’:
      skimage/_shared/transform.c:20543:25: error: ‘PyTypeObject’ {aka ‘struct _typeobject’} has no member named ‘tp_print’
      20543 |   __pyx_type___pyx_array.tp_print = 0;
            |                         ^
      skimage/_shared/transform.c:20548:31: error: ‘PyTypeObject’ {aka ‘struct _typeobject’} has no member named ‘tp_print’
      . . .
      Failed to build scikit-image
      . . .
```

so try bumping skikit-image to 0.15.0:
`(from versions: 0.7.2, 0.8.0, 0.8.1, 0.8.2,
0.9.0, 0.9.1, 0.9.3, 0.10.0, 0.10.1, 0.11.2, 0.11.3, 0.12.0, 0.12.1,
0.12.2, 0.12.3, 0.13.0, 0.13.1, 0.14.0, 0.14.1, 0.14.2, 0.14.3, 0.14.5,
0.15.0, 0.16.2, 0.17.1, 0.17.2, 0.18.0, 0.18.1, 0.18.2, 0.18.3,
0.19.0rc0, 0.19.0, 0.19.1, 0.19.2, 0.19.3, 0.20.0.dev0, 0.20.0rc2,
0.20.0rc3, 0.20.0rc4, 0.20.0rc5, 0.20.0rc6, 0.20.0rc7, 0.20.0rc8,
0.20.0)`


result:
```
  Preparing metadata (setup.py) ... error
  error: subprocess-exited-with-error

  × python setup.py egg_info did not run successfully.
  │ exit code: 1
  ╰─> [6 lines of output]
      Traceback (most recent call last):
        File "<string>", line 2, in <module>
        File "<pip-setuptools-caller>", line 34, in <module>
        File "/tmp/pip-install-cnxrj_r0/scikit-image_9ce4843714df4b73816e4c639592d7fd/setup.py", line 31, in <module>
          from numpy.distutils.command.build_ext import build_ext
      ModuleNotFoundError: No module named 'numpy'
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
error: metadata-generation-failed

× Encountered error while generating package metadata.
╰─> See above for output.

note: This is an issue with the package mentioned above, not pip.
hint: See above for details.
```
so try:
- `$PIP install numpy==1.21.6` first, then try 0.15.0 again.
  result:
```
. . .
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h:55:20: error: ‘__W’ is used uninitialized [-W[redacted]=uninitialized]
         55 |   return (__m512d) __builtin_ia32_exp2pd_mask ((__v8df) __A,
            |                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
         56 |                                                (__v8df) __W,
            |                                                ~~~~~~~~~~~~~
         57 |                                                (__mmask8) -1, __R);
            |                                                ~~~~~~~~~~~~~~~~~~~
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h: In function ‘main’:
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h:54:11: note: ‘__W’ was declared here
         54 |   __m512d __W;
            |           ^~~
      In file included from /usr/lib/gcc/x86_64-redhat-linux/12/include/immintrin.h:53:
      In function ‘_mm512_mask_prefetch_i64scatter_pd’,
          inlined from ‘main’ at /home/owner/.virtualenvs/deepfacelab/lib/python3.9/site-packages/numpy/distutils/checks/cpu_avx512_knl.c:23:5:
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512pfintrin.h:180:3: error: ‘base’ may be used uninitialized [-W[redacted]=maybe-uninitialized]
        180 |   __builtin_ia32_scatterpfqpd (__mask, (__v8di) __index, __addr, __scale,
            |   ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
. . .
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h:55:20: error: ‘__W’ is used uninitialized [-W[redacted]=uninitialized]
         55 |   return (__m512d) __builtin_ia32_exp2pd_mask ((__v8df) __A,
            |                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
         56 |                                                (__v8df) __W,
            |                                                ~~~~~~~~~~~~~
         57 |                                                (__mmask8) -1, __R);
            |                                                ~~~~~~~~~~~~~~~~~~~
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h: In function ‘main’:
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512erintrin.h:54:11: note: ‘__W’ was declared here
         54 |   __m512d __W;
            |           ^~~
      In file included from /usr/lib/gcc/x86_64-redhat-linux/12/include/immintrin.h:53:
      In function ‘_mm512_mask_prefetch_i64scatter_pd’,
          inlined from ‘main’ at /home/owner/.virtualenvs/deepfacelab/lib/python3.9/site-packages/numpy/distutils/checks/cpu_avx512_knl.c:23:5:
      /usr/lib/gcc/x86_64-redhat-linux/12/include/avx512pfintrin.h:180:3: error: ‘base’ may be used uninitialized [-W[redacted]=maybe-uninitialized]
        180 |   __builtin_ia32_scatterpfqpd (__mask, (__v8di) __index, __addr, __scale,
            |   ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        181 |                                __hint);
            |                                ~~~~~~~
      <built-in>: In function ‘main’:
      <built-in>: note: by argument 3 of type ‘const void *’ to ‘__builtin_ia32_scatterpfqpd’ declared here
      /home/owner/.virtualenvs/deepfacelab/lib/python3.9/site-packages/numpy/distutils/checks/cpu_avx512_knl.c:18:9: note: ‘base’ declared here
         18 |     int base[128];
            |         ^~~~
      cc1: all warnings being treated as errors
. . .
error: legacy-install-failure

× Encountered error while trying to install package.
╰─> scikit-image
```
so try:

```
-scikit-image==0.14.2
+scikit-image==0.16.2
```
WORKS!
- Python 3.9.16

## System Requirements Troubleshooting
These troubleshooting steps were used to fix the requirements section so the requirements build would work.
- Not all of the steps may have been necessary, since missing parts may be replaceable and there were other problems as noted in the previous section.



The requirements "install the OS packages" part may cause:
```
 Problem 1: package libavcodec-free-devel-5.1.2-1.fc37.i686 requires libavcodec-free(x86-32) = 5.1.2-1.fc37, but none of the providers can be installed
  - conflicting requests
  - libavcodec-free-5.1.2-1.fc37.i686 has inferior architecture
```

So:

In my case, first do:
  `sudo dnf config-manager --disable download.opensuse.org_repositories`

then as per <https://discussion.fedoraproject.org/t/cant-install-codecs/73797> try:

```
sudo dnf distro-sync --refresh
```

got:
```
Error:
 Problem: problem with installed package webkitgtk6.0-2.40.0-1.fc37.x86_64
  - installed package webkitgtk6.0-2.40.0-1.fc37.x86_64 obsoletes webkit2gtk5.0 < 2.40.0-1.fc37 provided by webkit2gtk5.0-2.38.2-1.fc37.x86_64
  - package webkitgtk6.0-2.40.0-1.fc37.x86_64 obsoletes webkit2gtk5.0 < 2.40.0-1.fc37 provided by webkit2gtk5.0-2.38.2-1.fc37.x86_64
  - package telegram-desktop-4.3.1-1.fc37.x86_64 requires webkit2gtk5.0(x86-64), but none of the providers can be installed
  - problem with installed package telegram-desktop-4.7.1-1.fc37.x86_64
  - package telegram-desktop-4.7.1-1.fc37.x86_64 requires qt6-qtbase(x86-64) = 6.4.2, but none of the providers can be installed
  - qt6-qtbase-6.4.2-5.fc37.x86_64 does not belong to a distupgrade repository
(try to add '--skip-broken' to skip uninstallable packages)

```

`installed package webkitgtk6.0-2.40.0-1.fc37.x86_64 obsoletes webkit2gtk5.0 < 2.40.0-1.fc37 provided by webkit2gtk5.0-2.38.2-1.fc37.x86_64`
etc so:

`sudo dnf upgrade -y --obsoletes`

Then add --allowerasing to install line (See "install the OS packages")
which results in it working, but:
```
Removed:
  ffmpeg-5.1.2-9.fc37.x86_64                       ffmpeg-libs-5.1.2-9.fc37.x86_64
  libavdevice-5.1.2-9.fc37.x86_64                  obs-studio-28.1.2-3.fc37.x86_64
  shotcut-22.12.21-1.fc37.x86_64                   shotcut-langpack-en-22.12.21-1.fc37.noarch
  x264-0.164-3.20220602gitbaee400f.fc37.x86_64
```

## Not tried yet
- [ ] unrelated but may be useful: `libavcodec-freeworld` (Fedora)

- [ ] TODO:
```patch
-scikit-image==0.14.2
+scikit-image==0.14.3
```

It tries to use ninja, then falls back to Unix Makefile generation.
- TODO: Install the `ninja-build` package (For Fedora--may differ on other platforms, but is *not* the same as Ninja-IDE)

## Didn't work
- Install python3-opencv package for your distro, and remove opencv line from requirements.txt
  - Doesn't help since the problem is numpy

requirements-cuda.txt numpy line:
```patch
-numpy==1.19.3
+https://files.pythonhosted.org/packages/c5/21/275cfa7731ee2e121b1bf85ddb21b8712fe2f409f02a8b61521af6e4993d/numpy-1.24.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
```

