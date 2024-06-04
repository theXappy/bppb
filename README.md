# bppb
A bplist-protobuf polyglot creator.
Example output found [here](https://github.com/theXappy/bppb/raw/main/src/test/output.bppb).
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

## 👨‍🍳 CyberChef Recipe
Use this recipe to test the protobuf interpertation of the bppb output: [Click](https://gchq.github.io/CyberChef/#recipe=Protobuf_Decode('syntax%20%3D%20%22proto3%22;%5Cn%5Cnmessage%20Wrapper%20%7B%5Cn%20%20bytes%20HeaderPadding%20%3D%2012;%5Cn%20%20string%20Magic%20%3D%201;%5Cn%20%20bytes%20Payload%20%3D%202;%5Cn%20%20bytes%20FooterPadding%20%3D%203;%5Cn%7D',false,false)JPath_expression('Payload','%5C%5Cn',true)Find_/_Replace(%7B'option':'Regex','string':'%22'%7D,'',true,false,true,false)From_Base64('A-Za-z0-9%2B/%3D',true,false)Protobuf_Decode('//%20Place%20your%20payload%20schema%20here',false,false)&input=YnBsaXN0MDDWAQIDBAUGBwgJCgsMXxAvTG9uZ0tleTAwMDAxMTExMjIyMjMzMzM0NDQ0NTU1NTY2NjY3Nzc3ODg4ODk5OTlRYVFiUWNRZFFlQhM3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXxIAAAAcCgZCUFBCdjMSEAoOSGVsbG8sIFdvcmxkIX4adF8QP0FCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXowMTIzNDU2Nzg5IRB7CAkACBVHSUtNT1GO0NLT1AAAAAAAAAEBAAAAAAAAAA0AAAAAAAAAAAAAAAAAAADV)

