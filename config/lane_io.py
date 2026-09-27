"""Per-machine lane-file io (D-20260928-03(1) batch-1 writer dual-track).

Group decision D-20260928-03 lane migration: each machine additionally
writes its OWN lane file ``results/<face>.<machine>.json`` -- same
payload as the shared face plus a top-level ``lane_machine``
self-signature.  Shared files keep being written unchanged during the
compat dual-track window; the deterministic reader
(``scripts/merge_lane_views.py``) unions lane files with the legacy
blob using the conflict-resolver laws, so a swallowed shared write is
always recoverable from the owning machine's lane.

Laws carried:
  * r98 identity: machine id comes from ``fleet/machine.json`` ONLY --
    never guessed from file names or content.
  * fail-loud without breaking the writer's exit contract: a lane
    fault prints to stderr and returns False; the shared write already
    happened and stays authoritative during the window.
  * atomic os.replace; dict payloads only (fail-closed otherwise --
    all six A-faces are objects).
"""
import json
import os
import sys

from .settings import PATHS

_KNOWN_FACES = ("compute_audit", "regime_state", "autofill_state",
                "runnable_pool", "gate_attrition", "post_review_criteria")
_MID_CACHE = {"v": None}


def machine_id():
    """This machine's fleet id (r98: fleet/machine.json is the only
    source of identity; unreadable -> empty string, never a guess)."""
    if _MID_CACHE["v"] is None:
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), "fleet", "machine.json")
            with open(path, encoding="utf-8") as fh:
                _MID_CACHE["v"] = str(json.load(fh).get("machine_id", ""))
        except Exception:
            _MID_CACHE["v"] = ""
    return _MID_CACHE["v"]


def lane_path(face, machine=None):
    """results/<face>.<machine>.json (D-03(1) structural end-state)."""
    mid = machine if machine is not None else machine_id()
    return os.path.join(PATHS.results_dir, f"{face}.{mid}.json")


def write_lane(face, data, indent=1, machine=None):
    """Write this machine's lane file for ``face`` (atomic, superset of
    the shared payload + lane_machine).  Returns True on success; on
    fault prints to stderr and returns False -- never raises into the
    calling S6/tick writer (exit contracts are frozen)."""
    if face not in _KNOWN_FACES:
        print(f"lane_io: unknown face {face!r} -- refuse (fail-closed)",
              file=sys.stderr)
        return False
    if not isinstance(data, dict):
        print(f"lane_io: face {face!r} payload is "
              f"{type(data).__name__}, dict required -- refuse",
              file=sys.stderr)
        return False
    mid = machine if machine is not None else machine_id()
    if not mid:
        print("lane_io: machine_id unreadable (fleet/machine.json) -- "
              "refuse write (r98 identity law)", file=sys.stderr)
        return False
    payload = dict(data)
    payload["lane_machine"] = mid
    path = lane_path(face, mid)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            # default=str mirrors the regime face writer convention
            # (pandas/numpy scalars in probe payloads).
            json.dump(payload, fh, ensure_ascii=False, indent=indent,
                      default=str)
        os.replace(tmp, path)
        return True
    except Exception as ex:
        print(f"lane_io: lane write fault {path!r}: {ex} "
              f"(shared face stays authoritative)", file=sys.stderr)
        try:
            os.remove(tmp)
        except OSError:
            pass
        return False


def mirror_shared(face, indent=1, machine=None):
    """Seed/refresh a lane file from the current shared face (read ->
    write_lane).  Used to bootstrap faces whose writers are scattered
    one-off scripts; union semantics make the superset snapshot
    lossless for the reader."""
    shared = os.path.join(PATHS.results_dir, f"{face}.json")
    try:
        with open(shared, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"lane_io: shared face {face!r} absent -- nothing to "
              "mirror", file=sys.stderr)
        return False
    except Exception as ex:
        print(f"lane_io: shared face {face!r} unreadable: {ex} "
              f"(never mirror from a corrupt source)", file=sys.stderr)
        return False
    return write_lane(face, data, indent=indent, machine=machine)
