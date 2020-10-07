"""Test project to run PTABen tests."""
import typing as tp

import benchbuild as bb
from plumbum import local

from varats.project.project_util import (
    ProjectBinaryWrapper,
    wrap_paths_to_binaries,
    BinaryType,
)


class MicroBenchmark(bb.Project):  # type: ignore
    """
    Get examples from PTABen: Micro-benchmark Suite for Pointer Analysis

    Source: https://github.com/SVF-tools/Test-Suite
    """

    NAME = 'svf'
    DOMAIN = 'c_projects' # does also contain cpp projects
    GROUP = 'testbench'

    SOURCE = [
        bb.source.Git(
            remote="https://github.com/J03D03/Test-Suite.git",
            local="svf-test-suite",
            refspec="refs/remotes/origin/tests",
            limit=1, # None,
            shallow=False,
        )
    ]

    C_FILES = [
        "basic_c_tests/CI-funptr.c",
        "basic_c_tests/CI-local.c"
    ]

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        """Return a list of binaries generated by the project."""
        return wrap_paths_to_binaries([
            (file_name.replace('.c', ''), BinaryType.executable) for file_name in self.C_FILES
        ])

    def run_tests(self) -> None:
        pass

    def compile(self) -> None:
        source = local.path(self.source_of_primary)
        clang = bb.compiler.cc(self)
        with local.cwd(source):
            with local.env(CC=str(clang)):
                for file in self.C_FILES:
                    bb.watch(clang)(
                        "{source}/{file}".format(source=source, file=file), 
                        "-o", file.replace('.c', '')
                    )
                    