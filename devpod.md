## which provider you should use
You should use ssh provider instead of docker
I'm not sure why it does not work...

You can see the options by running `limactl show-ssh $(VM_NAME)`
and then add them in extra flags.
