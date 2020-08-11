"""
******************************************************************************
compas_rcf.docker
******************************************************************************

.. currentmodule:: compas_rcf.docker

Docker compose commands to be used from python scripts.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    compose_up
    compose_down
    restart_container
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import os
import shlex
import subprocess
import sys

from compas import IPY

log = logging.getLogger(__name__)


def _setup_env_vars(env_vars):
    list_vars = []
    for key in env_vars:
        if os.name == "nt":
            list_vars.append("set")
        list_vars.append("{}={}".format(key.upper(), env_vars[key]))
        list_vars.append("&&")

    return list_vars


def _run(cmd, check_output=False, print_output=True, **kwargs):
    if sys.version_info.major < 3:
        subprocess.call(cmd, universal_newlines=print_output, **kwargs)

        # TODO: Get check_call to work
        # if check_output:
        #     try:
        #         subprocess.check_call(cmd, universal_newlines=print_output, **kwargs)
        #     except subprocess.CalledProcessError as e:
        #         print("Error message: {}".format(e.cmd))
        #         raise
        # else:
        #     subprocess.call(cmd, universal_newlines=print_output, **kwargs)
    else:
        subprocess.run(cmd, check=check_output, text=print_output, **kwargs)


def compose_up(
    path,
    overrides=None,
    force_recreate=False,
    remove_orphans=False,
    ignore_orphans=True,
    print_output=True,
    check_output=True,
    env_vars=None,
):
    """Run ``docker-compose up`` for specified compose file.

    Parameters
    ----------
    path : :class:`os.PathLike`
        Path to compose file.
    overrides : :obj:`list` of :class:`os.PathLike`, optional
        Docker compose override files, e.g. ``docker-compose.override.yml``.
    force_recreate : :class:`bool`, optional
        Force recreation of containers specified in ``docker-compose`` file.
        Defaults to ``False``.
    remove_orphans : :class:`bool`, optional
        Remove orphaned containers. Defaults to ``False``.
    ignore_orphans : :class:`bool`, optional
        Don't warn about orphaned containers (useful since the use of multiple
        compose files produces false positives for this check). Defaults to
        ``True``.
    print_output : :class:`bool`, optional
        Print ``stdout`` and ``stdin`` generated by ``docker-compose`` command.
        Defaults to ``True``.
    check_output : :class:`bool`, optional
        Raise if ``docker-compose`` fails. Defaults to ``True``.
    env_vars : :class:`dict`, optional
        Environment variables to set before running ``docker-compose``
    """
    env_vars = env_vars if env_vars else {}

    run_kwargs = {}
    run_kwargs.update({"check_output": check_output})
    run_kwargs.update({"print_output": print_output})

    file_args = "--file {} ".format(path)

    for o_path in overrides or []:
        file_args += "--file {} ".format(o_path)

    cmd_str = "docker-compose {} up --detach".format(file_args)
    print(cmd_str)
    cmd = shlex.split(cmd_str, posix="win" not in sys.platform)
    print(cmd)
    log.debug("Env vars: {}".format(env_vars))

    if ignore_orphans:
        env_vars.update({"COMPOSE_IGNORE_ORPHANS": "true"})

    if len(env_vars) > 0:
        cmd = _setup_env_vars(env_vars) + cmd
        run_kwargs.update({"shell": True})

    if force_recreate:
        cmd.append("--force-recreate")

    if remove_orphans:
        cmd.append("--remove-orphans")

    log.debug("Command to run: {}".format(cmd))
    print("Command to run: {}".format(cmd))

    _run(cmd, **run_kwargs)


def compose_down(path, check_output=True, print_output=True):
    """Run ``docker-compose down`` for specified compose file.

    Parameters
    ----------
    path : :class:`os.PathLike` or :class:`str`
        Path to compose file
    print_output : :class:`bool`, optional
        Print ``stdout`` and ``stdin`` generated by ``docker-compose`` command.
        Defaults to ``True``.
    check_output : :class:`bool`, optional
        Raise if ``docker-compose`` fails. Defaults to ``True``.
    """
    cmd_str = 'docker-compose --file "{}" down'.format(path)
    cmd = shlex.split(cmd_str)

    log.debug("Running compose down for {}".format(path))

    _run(cmd, check_output=check_output, print_output=print_output)


def restart_container(container_name):
    """Run ``docker restart`` for specified container.

    Parameters
    ----------
    container_name : :class:`str`
        Name of container to restart.
    """
    func = _get_restart_container_func()
    return func(container_name)


def _get_restart_container_func():
    if IPY:
        return _restart_container_subprocess
    else:
        return _restart_container_dockerpy


def _restart_container_subprocess(container_name):
    cmd_str = 'docker-compose --file "{}" down'.format(container_name)
    cmd_str = 'docker restart "{}"'.format(container_name)
    cmd = shlex.split(cmd_str)

    log.debug("Restarting {}".format(container_name))

    _run(cmd)


def _restart_container_dockerpy(name):
    import docker

    with docker.client.from_env() as d:
        container = d.get(name)
        container.restart()