from importlib import import_module


def _has_edfapi():
    """Determine if a user has edfapi installed."""
    from ..edf.read_edf import has_edfapi
    return has_edfapi


def _check_edfapi():
    """Check if edfapi is installed."""
    if not _has_edfapi():
        raise RuntimeError('edfapi is not installed')


def requires_edfapi(func):
    """Skip testing if edfapi is not installed."""
    import pytest

    return pytest.mark.skipif(not _has_edfapi(), reason='Requires edfapi')(func)


def _check_pandas_installed(strict=True):
    """Aux function."""
    return _soft_import("pandas", "converting to dataframes", strict=strict)

def _check_mne_installed(strict=True):
    """Aux function."""
    return _soft_import("mne", "exporting to MNE", strict=strict)


def _soft_import(name, purpose, strict=True):
    """Import soft dependencies, providing informative errors on failure.

    Parameters
    ----------
    name : str
        Name of the module to be imported. For example, 'pandas'.
    purpose : str
        A very brief statement (formulated as a noun phrase) explaining what
        functionality the package provides to MNE-Python.
    strict : bool
        Whether to raise an error if module import fails.
    """

    # so that error msg lines are aligned
    def indent(x):
        return x.rjust(len(x) + 14)

    try:
        mod = import_module(name)
        return mod
    except (ImportError, ModuleNotFoundError):
        if strict:
            raise RuntimeError(
                f"For {purpose} to work, the {name} module is needed, "
                + "but it could not be imported.\n"
                + "\n".join(
                    (
                        indent(
                            "use the following installation method "
                            "appropriate for your environment:"
                        ),
                        indent(f"'pip install {name}'"),
                        indent(f"'conda install -c conda-forge {name}'"),
                    )
                )
            )
        else:
            return False
