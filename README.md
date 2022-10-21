This is a work-in-progress decoder/disassembler/decompiler for the .HBC (Hermes JavaScript bytecode) files, the Hermes VM being a C++-written JavaScript virtual machine used in various React Native-based applications, processing JavaScript files serialized in a binary format.

## Background

The Hermes VM for React Native was announced by Facebook on the [12 July 2019](https://engineering.fb.com/2019/07/12/android/hermes/). The initial release of Hermes was version 0.1.0 ([bytecode version 59](https://github.com/facebook/hermes/blob/v0.1.0/include/hermes/BCGen/HBC/BytecodeFileFormat.h#L32)), Github tags 0.0.1 to 0.0.3 correspond to pre-public release.

However, Hermes is the default compilation target for React Native on Android only since [React Native 0.70 (released on 5 September 2022)](https://reactnative.dev/blog/2022/09/05/version-070#hermes-as-default-engine), as explained [here](https://reactnative.dev/blog/2022/07/08/hermes-as-the-default).

Before that, and since React Native 0.60.2, the Hermes VM was an [opt-in feature](https://reactnative.dev/docs/hermes#enabling-hermes). Hermes for iOS is supported since [version 0.64 of React Native (release on the 12 March 2021)](https://reactnative.dev/blog/2021/03/12/version-0.64).

**React Native is used by a wide variety of significant mobile applications**, as exposed on the [React Native showcase page](https://reactnative.dev/showcase).

A variety of technical documentation regarding the Hermes VM, which is published as [an open-source](https://github.com/facebook/hermes/) project under the BSD license, including [various design documents in the Markdown format](https://github.com/facebook/hermes/tree/main/doc), which can be read on Github as well as on [Facebook's website for React documentation](https://hermesengine.dev/docs/vm/).

In Android applications released under the .APK format, the Hermes bytecode (HBC) file is usually located at:

```
$ file assets/index.android.bundle
assets/index.android.bundle: Hermes JavaScript bytecode, version 84
```

On non-Hermes based setups of React Native, this file usually contains minified/Webpacked JavaScript code.

## Dependencies

The application itself only relies on the Python 3.x standard library for now.

Certain internal development utilities may however require to install `libclang` for Python:

```
sudo apt install python3-clang-12
```
