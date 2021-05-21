"""Project to run tests from the micro-benchmark Test-Suite."""
import os
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
    Get examples from the Test-Suite micro-benchmark suite.

    Which can be found at https://github.com/SVF-tools/Test-Suite.
    """

    NAME = 'test_suite'
    GROUP = 'test_projects'
    DOMAIN = 'testing'

    SOURCE = [
        bb.source.Git(
            remote="https://github.com/SVF-tools/Test-Suite.git",
            local="svf-test-suite",
            refspec="HEAD",
            limit=1,  # None,
            shallow=False,
        )
    ]

    DIRS = [
        "basic_c_tests",
        "basic_cpp_tests",
        # "complex_tests",
        "cpp_types",
        "cs_tests",
        "fs_tests",
        # "fstbhc_tests",
        "path_tests",
        "graphtxt",
        # "mem_leak",
        # "mta",
        "non_annotated_tests",
        "path_tests",
    ]

    FILE_PATHS = []  # type: tp.List[str]

    def init_file_paths(self) -> None:
        """Initialize FILE_PATHS with .c and .cpp files found in DIRS."""
        source = os.getcwd() + '/tmp/' + self.source[0].local
        for directory in self.DIRS:
            for filename in os.listdir(source + '/' + directory):
                absolute_filepath = source + '/' + directory + '/' + filename
                ext = os.path.splitext(absolute_filepath)[1]
                if ext in ('.cpp', '.c'):
                    self.FILE_PATHS.append(directory + '/' + filename)

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        """Return a list of binaries generated by the project."""
        return wrap_paths_to_binaries([(
            file_name.replace('.cpp', '').replace('.c',
                                                  ''), BinaryType.executable
        ) for file_name in self.FILE_PATHS])

    def run_tests(self) -> None:
        pass

    def compile(self) -> None:
        source = local.path(self.source_of_primary)
        with local.cwd(source):
            for file in self.FILE_PATHS:
                arguments = [
                    f"{source}/{file}",
                    "-I{source}".format(source=source),
                    "-g",  # Generate source-level debug information
                    "-o",
                    file.with_suffix('')
                ]
                if os.path.splitext(file)[1] == '.c':
                    bb.watch(bb.compiler.cc(self))(arguments)
                else:
                    bb.watch(bb.compiler.cxx(self))(arguments)

    def __init__(self, var) -> None:
        super().__init__()
        self.init_file_paths()
