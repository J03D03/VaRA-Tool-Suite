"""Project file for libpng."""
import typing as tp

import benchbuild as bb
from benchbuild.utils.cmd import make, cmake, mkdir
from benchbuild.utils.revision_ranges import block_revisions, GoodBadSubgraph
from benchbuild.utils.settings import get_number_of_jobs
from plumbum import local

from varats.containers.containers import get_base_image, ImageBase
from varats.paper_mgmt.paper_config import project_filter_generator
from varats.project.project_util import (
    wrap_paths_to_binaries,
    ProjectBinaryWrapper,
    BinaryType,
    verify_binaries,
)
from varats.provider.cve.cve_provider import CVEProviderHook
from varats.utils.settings import bb_cfg


class Libpng(bb.Project, CVEProviderHook):  # type: ignore
    """
    Picture library.

    (fetched by Git)
    """

    NAME = 'libpng'
    GROUP = 'c_projects'
    DOMAIN = 'library'

    SOURCE = [
        block_revisions([
            GoodBadSubgraph(["8694cd8bf5f7d0d2739e503218eaf749c6cb7071"],
                            ["0e13545712dc39db5689452ff3299992fc0a8377"],
                            "missing generic symlink"),
            GoodBadSubgraph(["4491fa237ff21aa0bbccef52b4df25e05657fabd"],
                            ["715423c8d61fceea615b99d84aacdb546050fa99"],
                            "missing generic symlink"),
            GoodBadSubgraph(["0d5805822f8817a17937462a2fd0606ffdad378e"],
                            ["917648ecb92f45537924b3c46a4a811b956c7023"],
                            "build not atomatable"),
            GoodBadSubgraph(["917648ecb92f45537924b3c46a4a811b956c7023"], [
                "5b754aac0d59a5b4900360ed4e2e7dfaf1048ac8",
                "6611322a8b29103a160c971819f1c5a031cd9d4f"
            ], "cmake not available")
        ])(
            bb.source.Git(
                remote="https://github.com/glennrp/libpng.git",
                local="libpng",
                refspec="HEAD",
                limit=None,
                shallow=False,
                version_filter=project_filter_generator("libpng")
            )
        )
    ]

    CONTAINER = get_base_image(ImageBase.DEBIAN_10
                              ).run('apt', 'install', '-y', 'cmake')

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        """Return a list of binaries generated by the project."""
        return wrap_paths_to_binaries([
            ('build/libpng.so', BinaryType.shared_library)
        ])

    def run_tests(self) -> None:
        pass

    def compile(self) -> None:
        """Compile the project."""
        libpng_source = local.path(self.source_of(self.primary_source))

        compiler = bb.compiler.cc(self)
        mkdir(libpng_source / "build")
        with local.cwd(libpng_source / "build"):
            with local.env(CC=str(compiler)):
                bb.watch(cmake)("-G", "Unix Makefiles", "..")

            bb.watch(make)("-j", get_number_of_jobs(bb_cfg()))

        verify_binaries(self)

    @classmethod
    def get_cve_product_info(cls) -> tp.List[tp.Tuple[str, str]]:
        return [("Libpng", "Libpng")]
