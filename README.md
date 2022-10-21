This is a work-in-progress decoder/disassembler/decompiler for the .HBC (Hermes JavaScript bytecode) files, the Hermes VM being a C++-written JavaScript virtual machine used with various React Native-based applications, processing JavaScript file serialized in a binary format.

## Dependencies

The application itself only relies on the Python 3.x standard library for now.

Certain internal development utilities may however require to install `libclang` for Python:

```
sudo python3 install python3-pip
sudo pip3 install --upgrade clang
```
