"""Project to run tests from the micro-benchmark Test-Suite."""
import typing as tp
from pathlib import Path

import benchbuild as bb
from plumbum import local

from varats.project.project_util import (
    ProjectBinaryWrapper,
    wrap_paths_to_binaries,
    BinaryType,
)


class SVFPointsToAnalysisBenchmark(bb.Project):  # type: ignore
    """
    SVFPointsToAnalysisBenchmark provides an easy way to execute the examples
    from the Test-Suite micro-benchmark suite for testing points to analyses.

    Which can be found at https://github.com/SVF-tools/Test-Suite.
    """

    NAME = 'SVFPointsToBench'
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

    FILE_PATHS: tp.List[Path] = [
        # basic_c_tests
        Path("src/basic_c_tests/array-constIdx.c"),
        Path("src/basic_c_tests/array-varIdx2.c"),
        Path("src/basic_c_tests/array-varIdx.c"),
        Path("src/basic_c_tests/branch-call.c"),
        Path("src/basic_c_tests/branch-intra.c"),
        Path("src/basic_c_tests/CI-funptr.c"),
        Path("src/basic_c_tests/CI-global.c"),
        Path("src/basic_c_tests/CI-local.c"),
        Path("src/basic_c_tests/constraint-cycle-copy.c"),
        Path("src/basic_c_tests/constraint-cycle-field.c"),
        Path("src/basic_c_tests/constraint-cycle-pwc.c"),
        Path("src/basic_c_tests/field-ptr-arith-constIdx.c"),
        Path("src/basic_c_tests/field-ptr-arith-varIdx.c"),
        Path("src/basic_c_tests/funptr-global.c"),
        Path("src/basic_c_tests/funptr-nested-call.c"),
        Path("src/basic_c_tests/funptr-simple.c"),
        Path("src/basic_c_tests/funptr-struct.c"),
        Path("src/basic_c_tests/global-array.c"),
        Path("src/basic_c_tests/global-call-noparam.c"),
        Path("src/basic_c_tests/global-call-struct.c"),
        Path("src/basic_c_tests/global-call-twoparms.c"),
        Path("src/basic_c_tests/global-const-struct.c"),
        Path("src/basic_c_tests/global-funptr.c"),
        Path("src/basic_c_tests/global-initializer.c"),
        Path("src/basic_c_tests/global-nested-calls.c"),
        Path("src/basic_c_tests/global-simple.c"),
        Path("src/basic_c_tests/heap-indirect.c"),
        Path("src/basic_c_tests/heap-linkedlist.c"),
        Path("src/basic_c_tests/heap-wrapper.c"),
        Path("src/basic_c_tests/int2pointer.c"),
        Path("src/basic_c_tests/mesa.c"),
        Path("src/basic_c_tests/ptr-dereference1.c"),
        Path("src/basic_c_tests/ptr-dereference2.c"),
        Path("src/basic_c_tests/ptr-dereference3.c"),
        Path("src/basic_c_tests/spec-equake.c"),
        Path("src/basic_c_tests/spec-gap.c"),
        Path("src/basic_c_tests/spec-mesa.c"),
        Path("src/basic_c_tests/spec-parser.c"),
        Path("src/basic_c_tests/spec-vortex.c"),
        Path("src/basic_c_tests/struct-array.c"),
        Path("src/basic_c_tests/struct-assignment-direct.c"),
        Path("src/basic_c_tests/struct-assignment-indirect.c"),
        Path("src/basic_c_tests/struct-assignment-nested.c"),
        Path("src/basic_c_tests/struct-field-multi-dereference.c"),
        Path("src/basic_c_tests/struct-incompab-typecast.c"),
        Path("src/basic_c_tests/struct-incompab-typecast-nested.c"),
        Path("src/basic_c_tests/struct-instance-return.c"),
        Path("src/basic_c_tests/struct-nested-1-layer.c"),
        Path("src/basic_c_tests/struct-nested-2-layers.c"),
        Path("src/basic_c_tests/struct-nested-array1.c"),
        Path("src/basic_c_tests/struct-nested-array2.c"),
        Path("src/basic_c_tests/struct-nested-array3.c"),
        Path("src/basic_c_tests/struct-onefld.c"),
        Path("src/basic_c_tests/struct-simple.c"),
        Path("src/basic_c_tests/struct-twoflds.c"),

        # basic_cpp_tests
        Path("src/basic_cpp_tests/abstract.cpp"),
        Path("src/basic_cpp_tests/array-1.cpp"),
        Path("src/basic_cpp_tests/array-2.cpp"),
        Path("src/basic_cpp_tests/array-3.cpp"),
        Path("src/basic_cpp_tests/clean.sh"),
        Path("src/basic_cpp_tests/constructor-1.cpp"),
        Path("src/basic_cpp_tests/constructor-2.cpp"),
        Path("src/basic_cpp_tests/deque-1.cpp"),
        Path("src/basic_cpp_tests/deque-2.cpp"),
        Path("src/basic_cpp_tests/deque-3.cpp"),
        Path("src/basic_cpp_tests/deque-4.cpp"),
        Path("src/basic_cpp_tests/destructor-1.cpp"),
        Path("src/basic_cpp_tests/destructor-2.cpp"),
        Path("src/basic_cpp_tests/diamond-inheritance.cpp"),
        Path("src/basic_cpp_tests/dynamic_cast-1.cpp"),
        Path("src/basic_cpp_tests/forward_list-1.cpp"),
        Path("src/basic_cpp_tests/forward_list-2.cpp"),
        Path("src/basic_cpp_tests/forward_list-3.cpp"),
        Path("src/basic_cpp_tests/forward_list-4.cpp"),
        Path("src/basic_cpp_tests/func-ptr-in-class.cpp"),
        Path("src/basic_cpp_tests/global-obj-in-array.cpp"),
        Path("src/basic_cpp_tests/list-1.cpp"),
        Path("src/basic_cpp_tests/list-2.cpp"),
        Path("src/basic_cpp_tests/map-1.cpp"),
        Path("src/basic_cpp_tests/map-2.cpp"),
        Path("src/basic_cpp_tests/member-variable.cpp"),
        Path("src/basic_cpp_tests/pwc.cpp"),
        Path("src/basic_cpp_tests/queue-1.cpp"),
        Path("src/basic_cpp_tests/queue-2.cpp"),
        Path("src/basic_cpp_tests/set-1.cpp"),
        Path("src/basic_cpp_tests/set-2.cpp"),
        Path("src/basic_cpp_tests/single-inheritance-1.cpp"),
        Path("src/basic_cpp_tests/single-inheritance-2.cpp"),
        Path("src/basic_cpp_tests/single-inheritance-3.cpp"),
        Path("src/basic_cpp_tests/single-inheritance-4.cpp"),
        Path("src/basic_cpp_tests/stack-1.cpp"),
        Path("src/basic_cpp_tests/stack-2.cpp"),
        Path("src/basic_cpp_tests/unordered_map-1.cpp"),
        Path("src/basic_cpp_tests/unordered_map-2.cpp"),
        Path("src/basic_cpp_tests/unordered_set-1.cpp"),
        Path("src/basic_cpp_tests/variant-gep.cpp"),
        Path("src/basic_cpp_tests/vector-1.cpp"),
        Path("src/basic_cpp_tests/vector-2.cpp"),
        Path("src/basic_cpp_tests/vector-3.cpp"),
        Path("src/basic_cpp_tests/vector-4.cpp"),
        Path("src/basic_cpp_tests/virtual-call-simple.cpp"),
        Path("src/basic_cpp_tests/virtual-diamond-inheritance-2.cpp"),
        Path("src/basic_cpp_tests/virtual-inheritance-1.cpp"),
        Path("src/basic_cpp_tests/virtual-inheritance-2.cpp"),
        Path("src/basic_cpp_tests/virtual-inheritance-3.cpp"),

        # complex_test
        Path("src/complex_tests/cond-swap.c"),
        Path("src/complex_tests/instrument.sh"),
        Path("src/complex_tests/swap1.c"),
        Path("src/complex_tests/swap4.c"),
        Path("src/complex_tests/swap4-context1.c"),
        Path("src/complex_tests/swap4-context.c"),
        Path("src/complex_tests/swap4-contextindirect.c"),
        Path("src/complex_tests/swap-array.c"),
        Path("src/complex_tests/swap.c"),
        Path("src/complex_tests/swap-funcptr1.c"),
        Path("src/complex_tests/swap-funcptr2.c"),
        Path("src/complex_tests/swap-funcptr.c"),
        Path("src/complex_tests/swap-global1.c"),
        Path("src/complex_tests/swap-global2.c"),
        Path("src/complex_tests/swap-global.c"),
        Path("src/complex_tests/swap-heap1.c"),
        Path("src/complex_tests/swap-heap2.c"),
        Path("src/complex_tests/swap-heap3.c"),
        Path("src/complex_tests/swap-heap4.c"),
        Path("src/complex_tests/swap-heap.c"),
        Path("src/complex_tests/swap-indirect1.c"),
        Path("src/complex_tests/swap-indirect2.c"),
        Path("src/complex_tests/swap-indirect.c"),
        Path("src/complex_tests/swap-recursion.c"),
        Path("src/complex_tests/swap-struct1.c"),
        Path("src/complex_tests/swap-struct.c"),
        Path("src/complex_tests/swap-structindirect.c"),
        Path("src/complex_tests/test1.c"),
        Path("src/complex_tests/test1-path.c"),
        Path("src/complex_tests/test2.c"),
        Path("src/complex_tests/test2-path.c"),
        Path("src/complex_tests/test3.c"),
        Path("src/complex_tests/test3-path.c"),
        Path("src/complex_tests/test4.c"),
        Path("src/complex_tests/test5.c"),
        Path("src/complex_tests/test6.c"),
        Path("src/complex_tests/test8.c"),
        Path("src/complex_tests/test.c"),
        Path("src/complex_tests/test-clone1.c"),
        Path("src/complex_tests/test-clone.c"),
        Path("src/complex_tests/test-cond.c"),
        Path("src/complex_tests/test-globalstruct.c"),
        Path("src/complex_tests/test-indirect1.c"),
        Path("src/complex_tests/test-indirect.c"),
        Path("src/complex_tests/test-linklist1.c"),
        Path("src/complex_tests/test-linklist.c"),
        Path("src/complex_tests/test-path.c"),
        Path("src/complex_tests/test-recursive0.c"),
        Path("src/complex_tests/test-recursive1.c"),
        Path("src/complex_tests/test-recursive2.c"),
        Path("src/complex_tests/test-recursive.c"),
        Path("src/complex_tests/test-recursiveglobal1.c"),
        Path("src/complex_tests/test-recursiveglobal2.c"),
        Path("src/complex_tests/test-recursiveglobal.c"),

        # cs_tests
        Path("src/cs_tests/cs0.c"),
        Path("src/cs_tests/cs1.c"),
        Path("src/cs_tests/cs2.c"),
        Path("src/cs_tests/cs3.c"),
        Path("src/cs_tests/cs4.c"),
        Path("src/cs_tests/cs5.c"),
        Path("src/cs_tests/cs6.c"),
        Path("src/cs_tests/cs7.c"),
        Path("src/cs_tests/cs8.c"),
        Path("src/cs_tests/cs9.c"),
        Path("src/cs_tests/cs10.c"),
        Path("src/cs_tests/cs11.c"),
        Path("src/cs_tests/cs12.c"),
        Path("src/cs_tests/cs13.c"),
        Path("src/cs_tests/cs14.c"),
        Path("src/cs_tests/cs15.c"),
        Path("src/cs_tests/cs16.c"),
        Path("src/cs_tests/cs17.c"),
        Path("src/cs_tests/cs18.c"),
        Path("src/cs_tests/cs19.c"),
        Path("src/cs_tests/cs20.c"),
        Path("src/cs_tests/cs21.c"),
        Path("src/cs_tests/funcpoiner.c"),
        Path("src/cs_tests/recur0.c"),
        Path("src/cs_tests/recur2.c"),
        Path("src/cs_tests/recur3.c"),
        Path("src/cs_tests/recur4.c"),
        Path("src/cs_tests/recur5.c"),
        Path("src/cs_tests/recur6.c"),
        Path("src/cs_tests/recur7.c"),
        Path("src/cs_tests/recur8.c"),
        Path("src/cs_tests/recur9.c"),
        Path("src/cs_tests/recur10.c"),

        # fs_tests
        Path("src/fs_tests/array_alias_1.c"),
        Path("src/fs_tests/array_alias_2.c"),
        Path("src/fs_tests/array_alias_3.c"),
        Path("src/fs_tests/array_alias_4.c"),
        Path("src/fs_tests/array_alias_5.c"),
        Path("src/fs_tests/branch_1.c"),
        Path("src/fs_tests/branch_2.c"),
        Path("src/fs_tests/branch_3.c"),
        Path("src/fs_tests/function_pointer.c"),
        Path("src/fs_tests/function_pointer_2.c"),
        Path("src/fs_tests/global_1.c"),
        Path("src/fs_tests/global_2.c"),
        Path("src/fs_tests/global_3.c"),
        Path("src/fs_tests/global_4.c"),
        Path("src/fs_tests/global_5.c"),
        Path("src/fs_tests/pcycle1.c"),
        Path("src/fs_tests/pcycle2.c"),
        Path("src/fs_tests/return.c"),
        Path("src/fs_tests/simple_1.c"),
        Path("src/fs_tests/simple_2.c"),
        Path("src/fs_tests/simple_3.c"),
        Path("src/fs_tests/strong_update.c"),
        Path("src/fs_tests/struct_1.c"),
        Path("src/fs_tests/struct_2.c"),
        Path("src/fs_tests/test-su.c"),
        Path("src/fs_tests/tt.c"),

        # fstbhc_tests
        Path("src/fstbhc_tests/array1.c"),
        Path("src/fstbhc_tests/basic1.c"),
        Path("src/fstbhc_tests/constructor1.cpp"),
        Path("src/fstbhc_tests/field1.c"),
        Path("src/fstbhc_tests/field2.c"),
        Path("src/fstbhc_tests/field3.c"),
        Path("src/fstbhc_tests/loop.c"),
        Path("src/fstbhc_tests/static_first_field.cpp"),
        Path("src/fstbhc_tests/union.c"),
        Path("src/fstbhc_tests/virtual1.cpp"),
        Path("src/fstbhc_tests/virtual2.cpp"),
        Path("src/fstbhc_tests/virtual3.cpp"),
        Path("src/fstbhc_tests/xmalloc1.c"),
        Path("src/fstbhc_tests/xmalloc2.c"),
        Path("src/fstbhc_tests/xmalloc3.c"),

        # path_tests
        Path("src/path_tests/path1.c"),
        Path("src/path_tests/path2.c"),
        Path("src/path_tests/path3.c"),
        Path("src/path_tests/path4.c"),
        Path("src/path_tests/path5.c"),
        Path("src/path_tests/path6.c"),
        Path("src/path_tests/path7.c"),
        Path("src/path_tests/path8.c"),
        Path("src/path_tests/path9.c"),
        Path("src/path_tests/path10.c"),
        Path("src/path_tests/path11.c"),
        Path("src/path_tests/path12.c"),
        Path("src/path_tests/path13.c"),
        Path("src/path_tests/path14.c"),
        Path("src/path_tests/path15.c"),
        Path("src/path_tests/path16.c"),
        Path("src/path_tests/path17.c"),
        Path("src/path_tests/path18.c"),
        Path("src/path_tests/path19.c"),
        Path("src/path_tests/path20.c"),
        Path("src/path_tests/path21.c"),
        Path("src/path_tests/path22.c"),

        # mem_leak
        Path("src/mem_leak/malloc0.c"),
        Path("src/mem_leak/malloc1.c"),
        Path("src/mem_leak/malloc2.c"),
        Path("src/mem_leak/malloc3.c"),
        Path("src/mem_leak/malloc4.c"),
        Path("src/mem_leak/malloc5.c"),
        Path("src/mem_leak/malloc6.c"),
        Path("src/mem_leak/malloc7.c"),
        Path("src/mem_leak/malloc8.c"),
        Path("src/mem_leak/malloc9.c"),
        Path("src/mem_leak/malloc10.c"),
        Path("src/mem_leak/malloc11.c"),
        Path("src/mem_leak/malloc12.c"),
        Path("src/mem_leak/malloc13.c"),
        Path("src/mem_leak/malloc14.c"),
        Path("src/mem_leak/malloc15.c"),
        Path("src/mem_leak/malloc16.c"),
        Path("src/mem_leak/malloc17.c"),
        Path("src/mem_leak/malloc18.c"),
        Path("src/mem_leak/malloc19.c"),
        Path("src/mem_leak/malloc20.c"),
        Path("src/mem_leak/malloc21.c"),
        Path("src/mem_leak/malloc22.c"),
        Path("src/mem_leak/malloc23.c"),
        Path("src/mem_leak/malloc24.c"),
        Path("src/mem_leak/malloc25.c"),
        Path("src/mem_leak/malloc26.c"),
        Path("src/mem_leak/malloc27.c"),
        Path("src/mem_leak/malloc28.c"),
        Path("src/mem_leak/malloc29.c"),
        Path("src/mem_leak/malloc30.c"),
        Path("src/mem_leak/malloc31.c"),
        Path("src/mem_leak/malloc32.c"),
        Path("src/mem_leak/malloc33.c"),
        Path("src/mem_leak/malloc34.c"),
        Path("src/mem_leak/malloc35.c"),
        Path("src/mem_leak/malloc36.c"),
        Path("src/mem_leak/malloc37.c"),
        Path("src/mem_leak/malloc38.c"),
        Path("src/mem_leak/malloc39.c"),
        Path("src/mem_leak/malloc40.c"),
        Path("src/mem_leak/malloc41.c"),
        Path("src/mem_leak/malloc42.c"),
        Path("src/mem_leak/malloc43.c"),
        Path("src/mem_leak/malloc44.c"),
        Path("src/mem_leak/malloc45.c"),
        Path("src/mem_leak/malloc46.c"),
        Path("src/mem_leak/malloc47.c"),
        Path("src/mem_leak/malloc48.c"),
        Path("src/mem_leak/malloc49.c"),
        Path("src/mem_leak/malloc50.c"),
        Path("src/mem_leak/malloc51.c"),
        Path("src/mem_leak/malloc52.c"),
        Path("src/mem_leak/malloc53.c"),
        Path("src/mem_leak/malloc54.c"),
        Path("src/mem_leak/malloc55.c"),
        Path("src/mem_leak/malloc56.c"),
        Path("src/mem_leak/malloc57.c"),
        Path("src/mem_leak/malloc58.c"),
        Path("src/mem_leak/malloc59.c"),
        Path("src/mem_leak/malloc60.c"),
        Path("src/mem_leak/malloc61.c"),
        Path("src/mem_leak/malloc62.c"),
        Path("src/mem_leak/malloc63.c"),
        Path("src/mem_leak/malloc64.c"),
        Path("src/mem_leak/sp1.c"),
        Path("src/mem_leak/sp1a.c"),
        Path("src/mem_leak/sp22.c"),
        Path("src/mem_leak/sp2a.c"),
        Path("src/mem_leak/sp2.c"),
        Path("src/mem_leak/sp3a.c"),
        Path("src/mem_leak/sp3.c"),
        Path("src/mem_leak/sp41.c"),
        Path("src/mem_leak/sp4a.c"),
        Path("src/mem_leak/sp4.c"),
        Path("src/mem_leak/sp5a.c"),
        Path("src/mem_leak/sp5.c"),
        Path("src/mem_leak/sp6a.c"),
        Path("src/mem_leak/sp6.c"),
        Path("src/mem_leak/sp7.c"),
        Path("src/mem_leak/sp8.c"),
        Path("src/mem_leak/sp9.c"),
        Path("src/mem_leak/sp10.c"),
        Path("src/mem_leak/sp11.c"),
        Path("src/mem_leak/sp12a.c"),
        Path("src/mem_leak/sp12.c"),
        Path("src/mem_leak/sp13a.c"),
        Path("src/mem_leak/sp13.c"),
        Path("src/mem_leak/sp14a.c"),
        Path("src/mem_leak/sp14.c"),
        Path("src/mem_leak/sp15a.c"),
        Path("src/mem_leak/sp15.c"),

        # mta
        Path("src/mta/imprecise_cxt_indfork_1.c"),
        Path("src/mta/imprecise_cxt_indfork_2.c"),
        Path("src/mta/imprecise_cxt_indfork_3.c"),
        Path("src/mta/imprecise_cxt_join_4.c"),
        Path("src/mta/imprecise_cxt_join_5.c"),
        Path("src/mta/imprecise_cxt_loop_5.c"),
        Path("src/mta/imprecise_cxt_offspring_5.c"),
        Path("src/mta/imprecise_cxt_recur_2.c"),
        Path("src/mta/imprecise_cxt_recur_3.c"),
        Path("src/mta/imprecise_cxt_recur_5.c"),
        Path("src/mta/imprecise_cxt_recur_6.c"),
        Path("src/mta/imprecise_cxt_thdindex_3.c"),
        Path("src/mta/imprecise_cxt_thdindex_4_1.c"),
        Path("src/mta/imprecise_cxt_thdindex_4_2.c"),
        Path("src/mta/imprecise_cxt_thdindex_8_2.c"),
        Path("src/mta/imprecise_cxt_thdindex_9.c"),
        Path("src/mta/imprecise_cxt_thdindex_10.c"),
        Path("src/mta/succ_cxt_branch_1.c"),
        Path("src/mta/succ_cxt_branch_2.c"),
        Path("src/mta/succ_cxt_branch_3.c"),
        Path("src/mta/succ_cxt_branch_4.c"),
        Path("src/mta/succ_cxt_branch_5.c"),
        Path("src/mta/succ_cxt_cand_1.c"),
        Path("src/mta/succ_cxt_cand_2.c"),
        Path("src/mta/succ_cxt_cand_3.c"),
        Path("src/mta/succ_cxt_join_1.c"),
        Path("src/mta/succ_cxt_join_2.c"),
        Path("src/mta/succ_cxt_join_3.c"),
        Path("src/mta/succ_cxt_loop_1.c"),
        Path("src/mta/succ_cxt_loop_2.c"),
        Path("src/mta/succ_cxt_loop_3.c"),
        Path("src/mta/succ_cxt_loop_6.c"),
        Path("src/mta/succ_cxt_loop_8.c"),
        Path("src/mta/succ_cxt_offspring_1.c"),
        Path("src/mta/succ_cxt_offspring_2.c"),
        Path("src/mta/succ_cxt_offspring_3.c"),
        Path("src/mta/succ_cxt_offspring_4.c"),
        Path("src/mta/succ_cxt_recur_4.c"),
        Path("src/mta/succ_cxt_recur_7.c"),
        Path("src/mta/succ_cxt_recur_index_1.c"),
        Path("src/mta/succ_cxt_sibling_1.c"),
        Path("src/mta/succ_cxt_sibling_2.c"),
        Path("src/mta/succ_cxt_sibling_3.c"),
        Path("src/mta/succ_cxt_sibling_4.c"),
        Path("src/mta/succ_cxt_sibling_5.c"),
        Path("src/mta/succ_cxt_sibling_6.c"),
        Path("src/mta/succ_cxt_sibling_7.c"),
        Path("src/mta/succ_cxt_sibling_8.c"),
        Path("src/mta/succ_cxt_simple_1.c"),
        Path("src/mta/succ_cxt_simple_2.c"),
        Path("src/mta/succ_cxt_simple_3.c"),
        Path("src/mta/succ_cxt_synthesis_1.c"),
        Path("src/mta/succ_cxt_thdindex_2.c"),
        Path("src/mta/succ_cxt_thdindex_7.c"),
        Path("src/mta/succ_cxt_thdindex_8_1.c"),
        Path("src/mta/succ_cxt_thdindex_8_3.c"),
        Path("src/mta/succ_cxt_thdindex_8_4.c"),
        Path("src/mta/tt.c"),
        Path("src/mta/unsound_cxt_loop_7.c"),
        Path("src/mta/unsound_cxt_thdindex_6.c"),

        # path_tests
        Path("src/path_tests/path1.c"),
        Path("src/path_tests/path2.c"),
        Path("src/path_tests/path3.c"),
        Path("src/path_tests/path4.c"),
        Path("src/path_tests/path5.c"),
        Path("src/path_tests/path6.c"),
        Path("src/path_tests/path7.c"),
        Path("src/path_tests/path8.c"),
        Path("src/path_tests/path9.c"),
        Path("src/path_tests/path10.c"),
        Path("src/path_tests/path11.c"),
        Path("src/path_tests/path12.c"),
        Path("src/path_tests/path13.c"),
        Path("src/path_tests/path14.c"),
        Path("src/path_tests/path15.c"),
        Path("src/path_tests/path16.c"),
        Path("src/path_tests/path17.c"),
        Path("src/path_tests/path18.c"),
        Path("src/path_tests/path19.c"),
        Path("src/path_tests/path20.c"),
        Path("src/path_tests/path21.c"),
        Path("src/path_tests/path22.c"),
    ]

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        """Return a list of binaries generated by the project."""
        return wrap_paths_to_binaries([
            (str(file_name.with_suffix('')), BinaryType.executable)
            for file_name in self.FILE_PATHS
        ])

    def run_tests(self) -> None:
        pass

    def compile(self) -> None:
        """Compile the project."""
        source = local.path(self.source_of_primary)

        with local.cwd(source):
            for file in self.FILE_PATHS:
                arguments = [
                    f"{source}/{file}",
                    f"-I{source}",
                    "-g",  # Generate source-level debug information
                    "-S",  # Only run preprocess and compilation steps
                    "-o",
                    file.with_suffix('')
                ]
                if file.suffix == '.c':
                    bb.watch(bb.compiler.cc(self))(arguments)
                else:
                    bb.watch(bb.compiler.cxx(self))(arguments)
