"""Establish a shared Sherlock SSH connection with graphical authentication."""

import argparse
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys


HOSTS = {
    "login": "login.sherlock.stanford.edu",
    "dtn": "dtn.sherlock.stanford.edu",
}


def master_ready(socket: Path, destination: str) -> bool:
    """Check the local control socket without interactive authentication."""
    result = subprocess.run(
        ["ssh", "-S", str(socket), "-o", "BatchMode=yes", "-O", "check",
         destination],
        capture_output=True, text=True, timeout=20, check=False,
    )
    return result.returncode == 0


def connect(
    user: str,
    target: str,
    socket: Path,
    askpass: Path | None = None,
    status_only: bool = False,
) -> bool:
    """Authenticate through askpass and leave a checked SSH master available.

    Args:
        user: Stanford SUNet ID.
        target: login or dtn.
        socket: Shared SSH control socket path.
        askpass: Optional graphical authentication executable.
        status_only: Check access without attempting authentication.

    Returns:
        Whether a usable shared connection exists.

    Raises:
        ValueError: Invalid settings or unavailable graphical authentication.
        subprocess.CalledProcessError: Authentication fails or is cancelled.
    """
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", user):
        raise ValueError("Use your Stanford SUNet ID")
    if target not in HOSTS:
        raise ValueError("Target must be login or dtn")
    socket = socket.expanduser().absolute()
    if len(os.fsencode(socket)) > 100:
        raise ValueError("Socket paths must be at most 100 bytes")
    destination = f"{user}@{HOSTS[target]}"
    if master_ready(socket, destination):
        return True
    if status_only:
        return False
    if askpass is None:
        if sys.platform != "darwin":
            raise ValueError("Provide a graphical --askpass on this platform")
        askpass = Path(__file__).with_name("askpass.applescript")
    askpass = askpass.expanduser().resolve()
    if not askpass.is_file() or not os.access(askpass, os.X_OK):
        raise ValueError("The askpass helper must be an executable file")
    socket.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if socket.parent.stat().st_mode & 0o077:
        raise ValueError("Use a private socket directory (permissions 700)")
    environment = os.environ.copy()
    environment.update({
        "SSH_ASKPASS": str(askpass),
        "SSH_ASKPASS_REQUIRE": "force",
        "DISPLAY": environment.get("DISPLAY") or "sherlock-askpass",
    })
    subprocess.run(
        ["ssh", "-fMN", "-S", str(socket),
         "-o", "ControlMaster=yes", "-o", "ControlPersist=8h",
         "-o", "StrictHostKeyChecking=ask", "-o", "ConnectTimeout=20",
         "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=2",
         "-o", "ForwardAgent=no", "-o", "ForwardX11=no",
         "-o", "NumberOfPasswordPrompts=1", destination],
        env=environment, stdin=subprocess.DEVNULL, check=True, timeout=300,
    )
    return master_ready(socket, destination)


def main() -> None:
    """Connect or report the status of an existing Sherlock SSH master."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", required=True)
    parser.add_argument("--target", choices=HOSTS, default="login")
    parser.add_argument("--socket", type=Path)
    parser.add_argument("--askpass", type=Path)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    prefix = "sherlock" if args.target == "login" else "sherlock-dtn"
    socket = (args.socket or Path.home() / ".ssh" /
              f"{prefix}-{args.user}.sock").expanduser().absolute()
    try:
        ready = connect(
            args.user, args.target, socket, args.askpass, args.status,
        )
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Connection not established: {error}\n")
    if not ready:
        parser.exit(1, "No usable shared connection.\n")
    destination = f"{args.user}@{HOSTS[args.target]}"
    print(f"Connected. Shared socket: {socket}")
    command = "ssh" if args.target == "login" else "sftp"
    print(shlex.join([
        command, "-o", f"ControlPath={socket}", "-o", "BatchMode=yes",
        destination,
    ]))


if __name__ == "__main__":
    main()
