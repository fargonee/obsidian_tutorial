from utils.logger import log


def phase(name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            full_line = "# " + "=" * 115
            empty_line_left = "# " + "=" * 27
            empty_line_right = "=" * 27 + "#"

            # Phase banner
            log.magenta.bold(full_line)
            log.magenta.bold(full_line)
            log.magenta.bold(f"{empty_line_left} {name:^50} {empty_line_right}")
            log.magenta.bold(full_line)
            log.magenta.bold(full_line)

            return func(*args, **kwargs)
        return wrapper
    return decorator
