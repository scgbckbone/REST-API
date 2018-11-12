import sys
import logging


class InfoDebugFilter(logging.Filter):
    def filter(self, record):
        return record.levelno in (logging.DEBUG, logging.INFO)


def get_me_logger(name, path, form=None, stream=False, fh_level=logging.ERROR):
    l = logging.getLogger(name)
    l.setLevel(logging.DEBUG)
    fh = logging.FileHandler(path)
    fh.setLevel(fh_level)
    if not form:
        f_str = '%(asctime)s %(levelname)-15s %(name)-15s %(message)s'
        formatter = logging.Formatter(
            fmt=f_str,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        f_str = form
        formatter = logging.Formatter(
            fmt=f_str,
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    fh.setFormatter(formatter)
    l.addHandler(fh)

    if stream:
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.DEBUG)
        sh.addFilter(InfoDebugFilter())
        sh.setFormatter(formatter)
        l.addHandler(sh)

        sh_err = logging.StreamHandler()
        sh_err.setLevel(logging.WARNING)
        sh_err.setFormatter(formatter)
        l.addHandler(sh_err)

    return l


