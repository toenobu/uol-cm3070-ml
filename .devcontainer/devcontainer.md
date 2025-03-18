### mount
This section does not work.

```
  "volumes": [
    {
      "source": "/Users/${localEnv:USER}/.aws",
      "target": "/home/vscode/.aws",
      "type": "bind",
      "consistency": "cached"
    }
  ]
```

### reference
- https://code.visualstudio.com/remote/advancedcontainers/add-local-file-mount
