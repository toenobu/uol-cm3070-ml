### use pip instead of pipx
Initially, `sudo pipx ensurepath --global` failed
because the sudo user has an older pipx version without `--global` support.

I gave up using pipx and then I decided to use pip instead.

```
# this doesn't work
brew install pipx
pipx ensurepath
sudo pipx ensurepath --global # optional to allow pipx actions with --global argument
```

```
# but this commnad works as work around
sudo /usr/local/py-utils/bin/pipx ensurepath --global
```

### reference
https://github.com/pypa/pipx?tab=readme-ov-file#on-linux
