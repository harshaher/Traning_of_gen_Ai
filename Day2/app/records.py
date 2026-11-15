from data.sample_records import records


def load_records():

    return records


def search(records, keyword):

    results = []

    keyword = keyword.lower()

    for record in records:

        if keyword in str(record).lower():

            results.append(record)

    return results


def count_by(records, field="category"):

    categories = {

        "tar": "File Management",
        "ls": "File Management",
        "cd": "Navigation",
        "cp": "File Management",
        "mv": "File Management",
        "rm": "File Management",

        "chmod": "Permissions",
        "chown": "Permissions",

        "grep": "Search",
        "find": "Search",

        "df": "Disk Management",
        "du": "Disk Management",

        "ps": "Process Management",
        "kill": "Process Management",
        "top": "Process Management",

        "systemctl": "System Management",
        "journalctl": "System Management",

        "ssh": "Networking",
        "scp": "Networking",
        "curl": "Networking"

    }

    counts = {}

    for record in records:

        if field == "category":

            value = categories.get(record["command"], "Other")

        else:

            value = record.get(field, "Unknown")

        counts[value] = counts.get(value, 0) + 1

    return counts


def get_by_id(records, record_id):

    for record in records:

        if record["command"] == record_id:

            return record

    return None