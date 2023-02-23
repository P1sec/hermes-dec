`hermes-dec` is a reverse-engineering tool which can be used for disassembling and decompiling React Native files compiled into the Hermes VM bytecode (HBC) format.

For a wider presentation of its purpose, please see our [presentation blog post](https://labs.p1sec.com/?p=2070).

## Background

The Hermes VM for React Native was announced by Facebook on the [12 July 2019](https://engineering.fb.com/2019/07/12/android/hermes/). The initial release of Hermes was version 0.1.0 ([bytecode version 59](https://github.com/facebook/hermes/blob/v0.1.0/include/hermes/BCGen/HBC/BytecodeFileFormat.h#L32)), Github tags 0.0.1 to 0.0.3 correspond to pre-public release.

However, Hermes is the default compilation target for React Native on Android only since [React Native 0.70](https://reactnative.dev/blog/2022/09/05/version-070#hermes-as-default-engine) (released on 5 September 2022), as explained [here](https://reactnative.dev/blog/2022/07/08/hermes-as-the-default).

Before that, and since React Native 0.60.2, the Hermes VM was an [opt-in feature](https://reactnative.dev/docs/hermes#enabling-hermes). Hermes for iOS is supported since [version 0.64 of React Native](https://reactnative.dev/blog/2021/03/12/version-0.64) (released on the 12 March 2021).

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

## Usage

You can download the tool using the following command on Linux:

```
$ git clone git@github.com:P1sec/hermes-dec.git
$ cd hermes-dec/
```

For an Android application, you should extract the Hermes bundle file from the .APK file through using your favorite unzipping tool (an .APK file is a renamed .ZIP archive):

```
$ 7z x my_application.apk
$ cd my_application
```

And check the type of the `assets/index.android.bundle` React Native bundle file which, in the case of a React Native-based application, should be either a plain-text minified JavaScript bundle file or an Hermes bytecode file:

```
$ file assets/index.android.bundle
assets/index.android.bundle: Hermes JavaScript bytecode, version 84
```

If the concerned file is indeed an Hermes JavaScript bytecode file, you may then decode most of its file headers using the following utility (which output may not be stable over time):

```
~/hermes-dec/parsers/hbc_file_parser.py assets/index.android.bundle
```

You may then disassemble the contents of the React Native bytecode file to the `/tmp/my_output_file.hasm` output file using the following command (leave out the second parameter in order to send the disassembled content to the standard output):

```
~/hermes-dec/disassembly/hbc_disassembler.py assets/index.android.bundle /tmp/my_output_file.hasm
```

And perform the decompilation to pseudo-code (which is not valid JavaScript yet as it does not retranscribe loop/conditional structures) using the following command:

```
~/hermes-dec/decompilation/hbc_decompiler.py assets/index.android.bundle /tmp/my_output_file.js
```

## Extra documentation

You can find auto-generated documentation for the Hermes VM opcodes [here](https://p1sec.github.io/hermes-dec/opcodes_table.html).

This is an useful tool to understand the generated assembly code.
