# filur

filur is a CLI application for searching log files.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install filur.

## Usage

filur works by processing a playbook defined by the user. Each playbook can be configured to parse multiple log files and each of them with custom patterns. An example playbook is shown below, with comments to describe additional properties as well as descriptions of each parameter.

```
files:
  - file: "/home/kverqus/syslog"
    order_by: "weight"                  # "weight" or "none" (default). Optional
    direction: "forward"                # "forward" (default) or "reverse". Optional
    rows: 400                           # number of rows to process. All rows are processed if not specified. Optional
    patterns:
      - pattern: "DHCPREQUEST"          # the pattern the row will be searched for
        type: "string"                  # "string" or "regex"
        weight: 20                      # all matched patterns will have their weight combined
      - pattern: "x-pid"
        type: "string"
        weight: 50
        operator: "KEYWORD"             # "OR" (default if not specified), "AND", "NOT" or "KEYWORD". The "KEYWORD"
                                        # operator will only be evaluated on already matched rows
      - pattern: '"\d+"'                # regex pattern
        type: "regex"
        weight: 20
    output:
      type: "html"                      # "html", "json" or "console". "html" and "json" expects path to be specified
      path: "/home/kverqus/output.html"
      overwrite: true                   # if already existing file should be overwritten. Optional
```

```
kverqus@serenity:~# filur --playbook syslog.yaml
```