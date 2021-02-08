import json
import typing as tp
from datetime import datetime
from pathlib import Path

import benchbuild as bb
import yaml
from benchbuild import Experiment, Project, source
from benchbuild.experiment import ProjectT
from benchbuild.utils import actions
from benchbuild.utils.cmd import java, mkdir
from plumbum import local

from varats.base.version_header import VersionHeader
from varats.data.reports.szz_report import SZZReport, SZZUnleashedReport
from varats.provider.bug.bug_provider import BugProvider
from varats.report.report import FileStatusExtension as FSE
from varats.tools.research_tools.szz_unleashed import SZZUnleashed
from varats.utils.settings import bb_cfg
from varats.utils.yaml_util import store_as_yaml


class PrepareSZZUnleashedData(actions.Step):
    NAME = "PrepareSZZUnleashedData"
    DESCRIPTION = "Prepares data needed for running SZZUnleashed."

    def __init__(self, project: Project):
        super().__init__(obj=project, action_fn=self.prepare_szz_data)

    def prepare_szz_data(self) -> actions.StepResult:
        """Prepare data needed for running SZZUnleashed."""
        results_dir = Path(self.obj.source_of_primary).parent

        bug_provider = BugProvider.get_provider_for_project(self.obj)
        bugs = bug_provider.find_all_pygit_bugs()

        fixers_dict = {}
        for bug in bugs:
            # SZZUnleashed uses some strange timezone format that cannot be
            # produced by datetime, so we just fake it.
            commitdate = str(
                datetime.fromtimestamp(bug.fixing_commit.commit_time)
            ) + " +0000"
            creationdate = commitdate
            resolutiondate = commitdate
            # if bug.issue_id:
            # TODO: find issue creation/resolution date
            fixers_dict[str(bug.fixing_commit.id)] = {
                "hash": str(bug.fixing_commit.id),
                "commitdate": commitdate,
                "creationdate": creationdate,
                "resolutiondate": resolutiondate
            }

        with (results_dir / "issue_list.json").open("w") as issues_file:
            json.dump(fixers_dict, issues_file, indent=2)
        # print(json.dumps(fixers_dict, indent=2))

        return actions.StepResult.OK


class RunSZZUnleashed(actions.Step):
    NAME = "RunSZZUnleashed"
    DESCRIPTION = "Run SZZUnleashed on a project"

    def __init__(self, project: Project):
        super().__init__(obj=project, action_fn=self.run_szz)

    def run_szz(self) -> actions.StepResult:
        """Prepare data needed for running SZZUnleashed."""
        results_dir = Path(self.obj.source_of_primary).parent
        szzunleashed_jar = SZZUnleashed.install_location(
        ) / SZZUnleashed.get_jar_name()
        with local.cwd(results_dir):
            bb.watch(java)(
                "-jar", str(szzunleashed_jar), "-i",
                str(results_dir / "issue_list.json"), "-r",
                self.obj.source_of_primary
            )

        return actions.StepResult.OK


class CreateSZZUnleashedReport(actions.Step):
    NAME = "CreateSZZUnleashedReport"
    DESCRIPTION = "Run SZZUnleashed on a project"

    RESULT_FOLDER_TEMPLATE = "{result_dir}/{project_dir}"

    def __init__(self, project: Project):
        super().__init__(obj=project, action_fn=self.run_szz)

    def run_szz(self) -> actions.StepResult:
        """Prepare data needed for running SZZUnleashed."""
        if not self.obj:
            return actions.StepResult.ERROR
        project = self.obj

        # Add to the user-defined path for saving the results of the
        # analysis also the name and the unique id of the project of every
        # run.
        varats_result_folder = self.RESULT_FOLDER_TEMPLATE.format(
            result_dir=str(bb_cfg()["varats"]["outfile"]),
            project_dir=str(project.name)
        )
        mkdir("-p", varats_result_folder)

        bb_results_folder = Path(project.source_of_primary).parent
        with (bb_results_folder / "results" /
              "fix_and_introducers_pairs.json").open("r") as result_json:
            szz_result = json.load(result_json)
        bugs: tp.Dict[str, tp.Set[str]] = {}
        # entries are lists of the form [<fix>, <introducing>]
        for result_entry in szz_result:
            bugs.setdefault(result_entry[0], set())
            bugs[result_entry[0]].add(result_entry[1])
        bugs = {k: list(v) for k, v in bugs.items()}
        raw_szz_report = {"szz_tool": "SZZUnleashed", "bugs": bugs}

        result_file = SZZUnleashedReport.get_file_name(
            project_name=str(project.name),
            binary_name="",
            project_version=project.version_of_primary,
            project_uuid=str(project.run_uuid),
            extension_type=FSE.Success
        )

        with open(f"{varats_result_folder}/{result_file}", "w") as yaml_file:
            yaml_file.write(
                yaml.dump_all([
                    VersionHeader.from_version_number("SZZReport",
                                                      1).get_dict(),
                    raw_szz_report
                ],
                              explicit_start=True,
                              explicit_end=True)
            )

        return actions.StepResult.OK


class SZZUnleashedExperiment(Experiment):
    """Generates a SZZUnleashed report."""

    NAME = "SZZUnleashed"

    REPORT_TYPE = SZZReport

    @classmethod
    def sample(cls, prj_cls: ProjectT) -> tp.List[source.VariantContext]:
        variants = list(source.product(*prj_cls.SOURCE))
        return [source.context(*variants[0])]

    def actions_for_project(self, project: Project) -> tp.List[actions.Step]:
        """Returns the specified steps to run the project(s) specified in the
        call in a fixed order."""

        analysis_actions = [
            PrepareSZZUnleashedData(project),
            RunSZZUnleashed(project),
            CreateSZZUnleashedReport(project),
            actions.Clean(project)
        ]

        return analysis_actions
