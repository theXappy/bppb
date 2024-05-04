# bppb
A bplist-protobuf polyglot creator.
Exmaple output found [here](https://github.com/theXappy/bppb/raw/main/src/test/output.bppb).
![image](https://github.com/theXappy/bppb/assets/10898152/a61ff93a-46f2-4285-ab92-4f8752ec45af)


# How To
1. Clone the repo
2. run `bppb.py <bplist_file_path> <protobuf_file_path> <output_file_path>`

# Parsing the polyglot
The bplist input stays logically the same in the output file.  
Use any bplist parser the same way as you'd do with the input.

The protobuf input is embedded into another "wrapper" type.  
You can see the Wrapper's definition in `wrapper.proto`.  
Here are two choices of getting the original payload:
1. (Python only) Use `wrapper_pb2.py` from this repo and the `Wrapper` class from it.  
  Read the `Wrapper.Payload` bytes field and pass its value to your own message parser.
2. Modify `wrapper.proto` and edit the `Payload` field's type to your own, like this:  
  ```
syntax = "proto3";

message MyComplexProtobufMessage {
  string SomeField = 1;
  bytes SomeOtherField = 2;
}

message Wrapper {
  bytes HeaderPadding = 12;
  string Magic = 1;
  MyComplexProtobufMessage Payload = 2; // <-- Changed the type to my custom payload type
  bytes FooterPadding = 3;
}
```
then compile a new parser with `protoc` and use it to read `Wrapper.Payload`.  
This time the result will already be the same as the one you encoded in the input.
