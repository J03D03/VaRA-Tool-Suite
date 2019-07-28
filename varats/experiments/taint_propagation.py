"""
Execute showcase cpp examples with vara to analyse taints.

This class implements the full commit taint flow analysis (MTFA) graph generation of the variability-
aware region analyzer (VaRA).
"""

import typing as tp
from os import path

from plumbum import local
from plumbum import colors

from benchbuild.extensions import compiler, run, time
from benchbuild.settings import CFG
from benchbuild.project import Project
import benchbuild.utils.actions as actions
from benchbuild.utils.cmd import opt, mkdir, timeout

from varats.data.reports.empty_report import EmptyReport as ER
from varats.data.report import FileStatusExtension as FSE
from varats.data.revisions import get_proccessed_revisions
from varats.experiments.disassemble import Disassemble
from varats.experiments.extract import Extract
from varats.experiments.wllvm import RunWLLVM
from varats.settings import CFG as V_CFG
from varats.utils.experiment_util import (
    exec_func_with_pe_error_handler, FunctionPEErrorWrapper,
    VaRAVersionExperiment, PEErrorHandler)


class MTFAGraphGeneration(actions.Step):
    """
    Analyse a project with VaRA and generate a graph of the taint analysis.
    """

    NAME = "MTFAGraphGeneration"
    DESCRIPTION = "Analyses the bitcode with MTFA of VaRA."

    RESULT_FOLDER_TEMPLATE = "{result_dir}/{project_dir}"

    def __init__(self, project: Project):
        super(MTFAGraphGeneration, self).__init__(obj=project,
                                                  action_fn=self.analyze)

    def analyze(self) -> actions.StepResult:
        """
        This step performs the actual analysis with the correct flags.
        Flags:
            -print-MTFA: to run a taint flow analysis
            -yaml-out-file=<path>: specify the path to store the results
        """
        if not self.obj:
            return
        project = self.obj

        bc_cache_folder = local.path(Extract.BC_CACHE_FOLDER_TEMPLATE.format(
            cache_dir=str(CFG["vara"]["result"]),
            project_name=str(project.name)))

        # Add to the user-defined path for saving the results of the
        # analysis also the name and the unique id of the project of every
        # run.
        vara_result_folder = self.RESULT_FOLDER_TEMPLATE.format(
            result_dir=str(CFG["vara"]["outfile"]),
            project_dir=str(project.name))

        mkdir("-p", vara_result_folder)

        for binary_name in project.BIN_NAMES:
            result_file = ER.get_file_name(
                project_name=str(project.name),
                binary_name=binary_name,
                project_version=str(project.version),
                project_uuid=str(project.run_uuid),
                extension_type=FSE.Success)

        run_cmd = opt[
            "-vara-CD", "-print-Full-MTFA", "-S",
            "{ll_target_folder}/{ll_file}".
            format(ll_target_folder=Disassemble.LL_TARGET_FOLDER_TEMPLATE.format(
                project_builddir=str(project.builddir),
                project_src=str(project.SRC_FILE),
                project_name=str(project.name)),
                ll_file=Disassemble.LL_FILE_TEMPLATE.
                format(binary_name=str(binary_name))),
            "-o", "{res_folder}/{res_file}".
            format(res_folder=vara_result_folder, res_file=result_file
                   )]

        timeout_duration = '8h'

        exec_func_with_pe_error_handler(
            timeout[timeout_duration, run_cmd],
            PEErrorHandler(
                vara_result_folder,
                ER.get_file_name(
                    project_name=str(project.name),
                    binary_name=binary_name,
                    project_version=str(project.version),
                    project_uuid=str(project.run_uuid),
                    extension_type=FSE.Failed), run_cmd, timeout_duration))


class TaintPropagation(VaRAVersionExperiment):
    """
    Generates a taint flow analysis (MTFA) of the project(s) specified in the
    call.
    """

    NAME = "TaintPropagation"

    REPORT_TYPE = ER

    def actions_for_project(self, project: Project) -> tp.List[actions.Step]:
        """Returns the specified steps to run the project(s) specified in
        the call in a fixed order."""

        # Add the required runtime extensions to the project(s).
        project.runtime_extension = run.RuntimeExtension(project, self) \
            << time.RunWithTime()

        # Add the required compiler extensions to the project(s).
        project.compiler_extension = compiler.RunCompiler(project, self) \
            << RunWLLVM() \
            << run.WithTimeout()

        # Add own error handler to compile step
        project.compile = FunctionPEErrorWrapper(
            project.compile,
            PEErrorHandler(
                MTFAGraphGeneration.RESULT_FOLDER_TEMPLATE.format(
                    result_dir=str(CFG["vara"]["outfile"]),
                    project_dir=str(project.name)),
                ER.get_file_name(
                    project_name=str(project.name),
                    binary_name="all",
                    project_version=str(project.version),
                    project_uuid=str(project.run_uuid),
                    extension_type=FSE.CompileError),
            ))

        project.cflags = ["-fvara-handleRM=Commit"]

        analysis_actions = []

        analysis_actions.append(actions.Compile(project))
        analysis_actions.append(Disassemble(project))

        analysis_actions.append(MTFAGraphGeneration(project))
        # analysis_actions.append(actions.Clean(project))

        return analysis_actions
