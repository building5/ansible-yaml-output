# ansible-yaml-output

A [Ansible][] [plugin][] which works just like the default output, but prints
more readable YAML blocks instead of JSON.

## Usage

Copy this into your plugins directory. This is either
`ansible/plugins/callback`, or configured using the `callback_plugins` setting
in `ansible.cfg`.

Then add the following line to your `ansible.cfg`:

    stdout_callback = yaml_output

## License

[Apache License, v2.0](./LICENSE)


 [Ansible]: https://www.ansible.com/
 [plugin]: http://docs.ansible.com/ansible/developing_plugins.html
