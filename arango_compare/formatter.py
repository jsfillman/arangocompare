import os

def print_and_write(msg: str, output) -> None:
    print(msg)
    if output:
        output.write(msg + '\n')

def write_view_differences(differences, log_subdir):
    views_diff_file = os.path.join(log_subdir, "views.md")
    with open(views_diff_file, 'w') as f:
        f.write("# View Differences\n")
        for diff in differences:
            f.write(f"{diff}\n")
