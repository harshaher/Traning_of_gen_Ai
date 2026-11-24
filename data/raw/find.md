# find

> Find files or directories under a directory tree, recursively.
> More information: <https://www.gnu.org/software/findutils/manual/html_node/find_html/index.html>.

- Find files by extension:

`find {{root_path}} -name '{{*.ext}}'`

- Find all Python files:

`find . -type f -name "{{*.py}}"`

- Find directories matching a given name:

`find {{root_path}} -type d -name "{{directory_name}}"`

- Find files matching a given name, case-insensitively:

`find {{root_path}} -iname "{{*pattern*}}"`

- Find files matching a pattern, excluding specific paths:

`find {{root_path}} -name '{{*.py}}' -not -path '{{*/site-packages/*}}'`

- Find files larger than a specified size:

`find {{root_path}} -type f -size +{{100M}}`

- Find files modified in the last 7 days:

`find {{root_path}} -type f -mtime -{{7}}`

- Find files and execute a command on them:

`find {{root_path}} -type f -name '{{*.tmp}}' -delete`
