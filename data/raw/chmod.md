# chmod

> Change file access permissions.
> More information: <https://www.gnu.org/software/coreutils/manual/html_node/chmod-invocation.html>.

- Give the [u]ser who owns a file the right to e[x]ecute it:

`chmod u+x {{path/to/file}}`

- Give the [u]ser rights to [r]ead and [w]rite to a file/directory:

`chmod u+rw {{path/to/file_or_directory}}`

- Give [g]roup [r]ead access to a directory:

`chmod g+r {{path/to/directory}}`

- Give [a]ll users rights to [r]ead and e[x]ecute:

`chmod a+rx {{path/to/file}}`

- Set permissions using octal notation (750: owner rwx, group r-x, others none):

`chmod 750 {{path/to/file}}`

- Set read and write for owner, read for others (644):

`chmod 644 {{path/to/file}}`

- Recursively change permissions of a directory:

`chmod -R 755 {{path/to/directory}}`
