records = [

    {
        "command": "tar",
        "platform": "Linux",
        "description": "Create and extract archive files.",
        "example_task": "Create a compressed archive.",
        "example_command": "tar -czvf backup.tar.gz folder/",
        "source_url": "https://tldr.sh/linux/tar"
    },

    {
        "command": "ls",
        "platform": "Linux",
        "description": "List files and directories.",
        "example_task": "Display all files including hidden files.",
        "example_command": "ls -la",
        "source_url": "https://tldr.sh/linux/ls"
    },

    {
        "command": "cd",
        "platform": "Linux",
        "description": "Change the current directory.",
        "example_task": "Navigate to Documents.",
        "example_command": "cd Documents",
        "source_url": "https://tldr.sh/linux/cd"
    },

    {
        "command": "cp",
        "platform": "Linux",
        "description": "Copy files and directories.",
        "example_task": "Copy a file to another location.",
        "example_command": "cp file.txt backup.txt",
        "source_url": "https://tldr.sh/linux/cp"
    },

    {
        "command": "mv",
        "platform": "Linux",
        "description": "Move or rename files.",
        "example_task": "Rename a file.",
        "example_command": "mv old.txt new.txt",
        "source_url": "https://tldr.sh/linux/mv"
    },

    {
        "command": "rm",
        "platform": "Linux",
        "description": "Remove files or directories.",
        "example_task": "Remove a file after confirmation.",
        "example_command": "rm -i file.txt",
        "source_url": "https://tldr.sh/linux/rm"
    },

    {
        "command": "chmod",
        "platform": "Linux",
        "description": "Change file permissions.",
        "example_task": "Make a script executable.",
        "example_command": "chmod +x script.sh",
        "source_url": "https://tldr.sh/linux/chmod"
    },

    {
        "command": "chown",
        "platform": "Linux",
        "description": "Change file ownership.",
        "example_task": "Change file owner.",
        "example_command": "sudo chown user:group file.txt",
        "source_url": "https://tldr.sh/linux/chown"
    },

    {
        "command": "grep",
        "platform": "Linux",
        "description": "Search text using patterns.",
        "example_task": "Find a word inside a file.",
        "example_command": "grep -n 'hello' file.txt",
        "source_url": "https://tldr.sh/linux/grep"
    },

    {
        "command": "find",
        "platform": "Linux",
        "description": "Find files and directories.",
        "example_task": "Find all Python files.",
        "example_command": "find . -name '*.py'",
        "source_url": "https://tldr.sh/linux/find"
    },

    {
        "command": "df",
        "platform": "Linux",
        "description": "Display filesystem disk space.",
        "example_task": "Check available disk space.",
        "example_command": "df -h",
        "source_url": "https://tldr.sh/linux/df"
    },

    {
        "command": "du",
        "platform": "Linux",
        "description": "Display file and directory size.",
        "example_task": "Check folder size.",
        "example_command": "du -sh Documents/",
        "source_url": "https://tldr.sh/linux/du"
    },

    {
        "command": "ps",
        "platform": "Linux",
        "description": "Display running processes.",
        "example_task": "Show all running processes.",
        "example_command": "ps aux",
        "source_url": "https://tldr.sh/linux/ps"
    },

    {
        "command": "kill",
        "platform": "Linux",
        "description": "Send a signal to a process.",
        "example_task": "Terminate a process using its PID.",
        "example_command": "kill 1234",
        "source_url": "https://tldr.sh/linux/kill"
    },

    {
        "command": "top",
        "platform": "Linux",
        "description": "Monitor running processes and system resources.",
        "example_task": "Monitor CPU and memory usage.",
        "example_command": "top",
        "source_url": "https://tldr.sh/linux/top"
    },

    {
        "command": "systemctl",
        "platform": "Linux",
        "description": "Manage systemd services.",
        "example_task": "Check SSH service status.",
        "example_command": "systemctl status ssh",
        "source_url": "https://tldr.sh/linux/systemctl"
    },

    {
        "command": "journalctl",
        "platform": "Linux",
        "description": "View systemd journal logs.",
        "example_task": "View SSH service logs.",
        "example_command": "journalctl -u ssh",
        "source_url": "https://tldr.sh/linux/journalctl"
    },

    {
        "command": "ssh",
        "platform": "Linux",
        "description": "Connect to a remote machine securely.",
        "example_task": "Connect to a remote server.",
        "example_command": "ssh user@192.168.1.10",
        "source_url": "https://tldr.sh/linux/ssh"
    },

    {
        "command": "scp",
        "platform": "Linux",
        "description": "Copy files securely between computers.",
        "example_task": "Upload a file to a remote server.",
        "example_command": "scp file.txt user@server:/home/user/",
        "source_url": "https://tldr.sh/linux/scp"
    },

    {
        "command": "curl",
        "platform": "Linux",
        "description": "Transfer data using URLs.",
        "example_task": "Check website HTTP headers.",
        "example_command": "curl -I https://example.com",
        "source_url": "https://tldr.sh/linux/curl"
    }

]