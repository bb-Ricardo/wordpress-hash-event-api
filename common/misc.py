import sys

def do_error_exit(log_text):
    """
    log an error and exit with return code 1
    Parameters
    ----------
    log_text : str
        the text to log as error
    """

    print(log_text, file=sys.stderr)
    exit(1)
