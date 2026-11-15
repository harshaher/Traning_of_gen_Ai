while True:
    print("\n====== ShellSathi Menu ======")
    print("1. About ShellSathi")
    print("2. Sample Questions")
    print("3. Linux Command Rule Check")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        print("\nShellSathi is a Linux command assistant.")
        print("It helps beginners learn Linux commands.")

    elif choice == "2":
        print("\nSample Questions:")
        print("1. How to list files?")
        print("2. How to create a folder?")
        print("3. How to check current directory?")

    elif choice == "3":
        command = input("Enter a Linux command: ")

        if command == "ls":
            print("Correct! ls lists files and directories.")
        elif command == "pwd":
            print("Correct! pwd displays the current directory.")
        elif command == "cd":
            print("Correct! cd changes the directory.")
        else:
            print("Command not available in this beginner rule check.")

    elif choice == "0":
        print("Thank you for using ShellSathi!")
        break

    else:
        print("Invalid choice. Please try again.")