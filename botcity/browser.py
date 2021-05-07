import webbrowser


def browse(url, location=0):
    """
    Invoke the default browser passing an URL

    Args:
        url (str):  The URL to be visited.
        location (int): If possible, open url in a location determined by new:
                        * 0: the same browser window (the default)
                        * 1: a new browser window
                        * 2: a new browser page ("tab")

    Returns:
        bool: Whether or not the request was successful
    """
    status = webbrowser.open(url, location)
    return status
