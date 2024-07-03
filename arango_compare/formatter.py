def print_and_write(msg: str, output) -> None:
    print(msg)
    if output:
        output.write(msg + '\n')
