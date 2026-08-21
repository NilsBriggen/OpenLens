"""
Filesystem locations for OpenLens runtime state.

Production deployments keep state in system-wide directories such as
/etc/openlens and /var/data/openlens. Those are not writable by an unprivileged
developer checkout, and several modules create their directories while being
imported, so a hardcoded system path takes the whole API down at startup.

Each location therefore resolves in three steps:

1. an explicit environment variable, when set;
2. the system-wide default, when it is writable;
3. a per-user directory under $XDG_STATE_HOME (or ~/.local/state).

Production behaviour is unchanged - step 2 succeeds when running as root or
against pre-provisioned directories.
"""

import os
from pathlib import Path

__all__ = ['resolve_dir', 'resolve_file', 'user_state_root']


def user_state_root() -> Path:
    """Per-user base directory for OpenLens state."""
    xdg_state_home = os.environ.get('XDG_STATE_HOME')
    base = Path(xdg_state_home) if xdg_state_home else Path.home() / '.local' / 'state'
    return base / 'openlens'


def _is_writable(path: Path) -> bool:
    """
    True when `path` is writable, or when its nearest existing ancestor is and
    the missing part could therefore be created.
    """
    candidate = path
    while not candidate.exists():
        parent = candidate.parent
        if parent == candidate:
            return False
        candidate = parent

    return candidate.is_dir() and os.access(candidate, os.W_OK)


def resolve_dir(env_var: str, system_default: str, fallback_subdir: str) -> str:
    """
    Resolve a state directory.

    Args:
        env_var: Environment variable that overrides the location outright.
        system_default: System-wide path used in production.
        fallback_subdir: Directory under the per-user state root to use when the
            system-wide path is not writable.

    Returns:
        Absolute path as a string. The directory is not created here.
    """
    override = os.environ.get(env_var)
    if override:
        return override

    if _is_writable(Path(system_default)):
        return system_default

    return str(user_state_root() / fallback_subdir)


def resolve_file(env_var: str, system_default: str, fallback_relpath: str) -> str:
    """
    Resolve a state file, applying `resolve_dir` logic to its parent directory.

    Args:
        env_var: Environment variable that overrides the location outright.
        system_default: System-wide file path used in production.
        fallback_relpath: Path relative to the per-user state root to use when
            the system-wide location is not writable.

    Returns:
        Absolute path as a string. The file is not created here.
    """
    override = os.environ.get(env_var)
    if override:
        return override

    if _is_writable(Path(system_default).parent):
        return system_default

    return str(user_state_root() / fallback_relpath)
