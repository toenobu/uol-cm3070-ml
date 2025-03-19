

### reference to uv
https://docs.astral.sh/uv/guides/integration/aws-lambda/
https://docs.astral.sh/uv/getting-started/features/

### reference to onnx-on-aws-lambda-arm64
https://github.com/DiscreteTom/onnx-on-aws-lambda-arm64

on arm64 lambda you will get the following error:

```
Error in cpuinfo: failed to parse the list of possible processors in /sys/devices/system/cpu/possible
Error in cpuinfo: failed to parse the list of present processors in /sys/devices/system/cpu/present
Error in cpuinfo: failed to parse both lists of possible and present processors
```

> Why can't you generate /sys/devices/system/cpu/possible and /sys/devices/system/cpu/present during the runtime to write the correct vCPU count? That's because in Lambda only /tmp is writable. Thus you have to finish the patch process before the Lambda is invoked.

it still glitch it keeps working even if there are such errors.
I ended up not adding the patch.
