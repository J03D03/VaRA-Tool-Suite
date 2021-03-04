"""Project file for the GNU grep."""
import typing as tp

import benchbuild as bb
from benchbuild.utils.cmd import make
from benchbuild.utils.settings import get_number_of_jobs
from plumbum import local

from varats.paper_mgmt.paper_config import project_filter_generator
from varats.project.project_util import (
    wrap_paths_to_binaries,
    ProjectBinaryWrapper,
    BinaryType,
    verify_binaries,
)
from varats.provider.cve.cve_provider import CVEProviderHook
from varats.utils.settings import bb_cfg


class Grep(bb.Project, CVEProviderHook):  # type: ignore
    """GNU Grep / UNIX command-line tools (fetched by Git)"""

    NAME = 'grep'
    GROUP = 'c_projects'
    DOMAIN = 'utils'

    SOURCE = [
        bb.source.Git(
            remote="https://github.com/vulder/grep.git",
            local="grep",
            refspec="HEAD",
            limit=None,
            shallow=False,
            version_filter=project_filter_generator("grep")
        ),
        bb.source.GitSubmodule(
            remote="https://github.com/coreutils/gnulib.git",
            local="grep/gnulib",
            refspec="HEAD",
            limit=None,
            shallow=False,
            version_filter=project_filter_generator("grep")
        )
    ]

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        """Return a list of binaries generated by the project."""

        return wrap_paths_to_binaries([
            ("src/grep", BinaryType.executable),
        ])

    def run_tests(self) -> None:
        grep_source = local.path(self.source_of_primary)
        with local.cwd(grep_source):
            bb.watch(make)("-j", get_number_of_jobs(bb_cfg()), "check")

    def compile(self) -> None:
        grep_source = local.path(self.source_of_primary)
        compiler = bb.compiler.cc(self)
        with local.cwd(grep_source):
            with local.env(CC=str(compiler)):
                bb.watch(local["./bootstrap"])()
                bb.watch(local["./configure"])("--disable-gcc-warnings")

            bb.watch(make)("-j", get_number_of_jobs(bb_cfg()))

            verify_binaries(self)

    @classmethod
    def get_cve_product_info(cls) -> tp.List[tp.Tuple[str, str]]:
        return [("gnu", "grep")]