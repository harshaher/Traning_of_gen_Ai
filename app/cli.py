from app.records import (
    load_records,
    search,
    count_by,
    get_by_id
)


def main():

    records = load_records()

    while True:

        print("\n===== ShellSathi CLI =====")

        print("1. Show all commands")
        print("2. Search command")
        print("3. Count by category")
        print("4. Get command by ID")
        print("0. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":

            for record in records:

                print("\n", record)

        elif choice == "2":

            keyword = input("Enter keyword: ")

            results = search(records, keyword)

            if results:

                for record in results:

                    print("\n", record)

            else:

                print("No records found.")

        elif choice == "3":

            counts = count_by(records)

            print("\nCategory Counts:")

            for category, total in counts.items():

                print(category, ":", total)

        elif choice == "4":

            command = input("Enter command name: ")

            result = get_by_id(records, command)

            if result:

                print("\n", result)

            else:

                print("Command not found.")

        elif choice == "0":

            print("Thank you for using ShellSathi!")

            break

        else:

            print("Invalid choice. Try again.")


if __name__ == "__main__":

    main()