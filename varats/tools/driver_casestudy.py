"""
Driver module for `vara-cs`.
"""

import logging
import os
import re
import typing as tp
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
import subprocess

from argparse_utils import enum_action

from plumbum import FG
from benchbuild.utils.cmd import find

from varats.data.report import MetaReport
from varats.paper import paper_config_manager as PCM
from varats.paper.case_study import (SamplingMethod, ExtenderStrategy,
                                     ReleaseType, load_case_study_from_file,
                                     extend_case_study, store_case_study,
                                     generate_case_study)
from varats.settings import CFG
from varats.tools.commit_map import create_lazy_commit_map_loader
from varats.utils.project_util import get_local_project_git_path

LOG = logging.getLogger(__name__)


def main() -> None:
    """
    Allow easier management of case studies
    """
    parser = ArgumentParser("vara-cs")
    sub_parsers = parser.add_subparsers(help="Subcommand", dest="subcommand")

    # vara-cs status
    status_parser = sub_parsers.add_parser(
        'status', help="Show status of current case study")
    status_parser.add_argument(
        "report_name",
        help=("Provide a report name to "
              "select which files are considered for the status"),
        choices=MetaReport.REPORT_TYPES.keys(),
        type=str,
        default=".*")
    status_parser.add_argument(
        "--filter-regex",
        help="Provide a regex to filter the shown case studies",
        type=str,
        default=".*")
    status_parser.add_argument(
        "--paper_config",
        help="Use this paper config instead of the configured one",
        default=None)
    status_parser.add_argument("-s",
                               "--short",
                               help="Only print a short summary",
                               action="store_true",
                               default=False)
    status_parser.add_argument(
        "--list-revs",
        help="Print a list of revisions for every stage and every case study",
        action="store_true",
        default=False)
    status_parser.add_argument("--ws",
                               help="Print status with stage separation",
                               action="store_true",
                               default=False)
    status_parser.add_argument(
        "--sorted",
        help="Sort the revisions in the order they are printed by git log.",
        action="store_true",
        default=False)
    status_parser.add_argument("--legend",
                               help="Print status with legend",
                               action="store_true",
                               default=False)

    def add_common_args(sub_parser: ArgumentParser) -> None:
        """
        Group common args to provide all args on different sub parsers.
        """
        sub_parser.add_argument("--git-path",
                                help="Path to git repository",
                                default=None)
        sub_parser.add_argument("-p",
                                "--project",
                                help="Project name",
                                default=None)
        sub_parser.add_argument("--end",
                                help="End of the commit range (inclusive)",
                                default="HEAD")
        sub_parser.add_argument("--start",
                                help="Start of the commit range (exclusive)",
                                default=None)
        sub_parser.add_argument(
            "--extra-revs",
            nargs="+",
            default=[],
            help="Add a list of additional revisions to the case-study")
        sub_parser.add_argument(
            "--revs-per-year",
            type=int,
            default=0,
            help="Add this many revisions per year to the case-study.")
        sub_parser.add_argument(
            "--revs-year-sep",
            action="store_true",
            default=False,
            help="Separate the revisions in different stages per year "
            "(when using \'--revs-per-year\').")
        sub_parser.add_argument("--num-rev",
                                type=int,
                                default=10,
                                help="Number of revisions to select.")

    # vara-cs gen
    gen_parser = sub_parsers.add_parser('gen', help="Generate a case study.")
    gen_parser.add_argument(
        "paper_config_path",
        help="Path to paper_config folder (e.g., paper_configs/ase-17)")

    gen_parser.add_argument("distribution", action=enum_action(SamplingMethod))
    gen_parser.add_argument("-v",
                            "--version",
                            type=int,
                            default=0,
                            help="Case study version.")
    add_common_args(gen_parser)

    # vara-cs ext
    ext_parser = sub_parsers.add_parser('ext',
                                        help="Extend an existing case study.")
    ext_parser.add_argument("case_study_path", help="Path to case_study")
    ext_parser.add_argument("strategy",
                            action=enum_action(ExtenderStrategy),
                            help="Extender strategy")
    ext_parser.add_argument("--distribution",
                            action=enum_action(SamplingMethod))
    ext_parser.add_argument("--release-type", action=enum_action(ReleaseType))
    ext_parser.add_argument(
        "--merge-stage",
        default=-1,
        type=int,
        help="Merge the new revision into stage `n`, defaults to last stage. " +
        "Use '+' to add a new stage.")
    ext_parser.add_argument(
        "--boundary-gradient",
        type=int,
        default=5,
        help="Maximal expected gradient in percent between " +
        "two revisions, e.g., 5 for 5%%")
    ext_parser.add_argument("--plot-type",
                            help="Plot to calculate new revisions from.")
    ext_parser.add_argument("--report-type",
                            help="Passed to the plot given via --plot-type.",
                            default="EmptyReport")
    ext_parser.add_argument(
        "--result-folder",
        help="Maximal expected gradient in percent between two revisions")
    add_common_args(ext_parser)

    # vara-cs view
    view_parser = sub_parsers.add_parser(
        'view', help="View a file of one revision for the current case study")

    view_parser.add_argument(
        "report_name",
        help=("Provide a report name to "
              "select which files are considered you want to view"),
        choices=MetaReport.REPORT_TYPES.keys(),
        type=str,
        default=".*")

    view_parser.add_argument(
        "commit_hash",
        help=("Provide a commit hash to select which revisions are shown"),
        # TODO get a list of commits per report, problem depends on report
        # choices=get_processed_revisions(),
        type=str,
        default="*")

    # vara-cs package
    package_parser = sub_parsers.add_parser('package',
                                            help="Case study packaging util")
    package_parser.add_argument("-o", "--output", help="Output file")
    package_parser.add_argument("--filter-regex",
                                help="Provide a regex to only include case "
                                "studies that match the filter.",
                                type=str,
                                default=".*")
    package_parser.add_argument(
        "--report_names",
        help=("Provide a report name to "
              "select which files are considered for the status"),
        choices=MetaReport.REPORT_TYPES.keys(),
        type=str,
        nargs="*",
        default=[])

    args = {k: v for k, v in vars(parser.parse_args()).items() if v is not None}

    if 'subcommand' not in args:
        parser.print_help()
        return

    if args['subcommand'] == 'status':
        __casestudy_status(args, parser)
    elif args['subcommand'] == 'gen' or args['subcommand'] == 'ext':
        __casestudy_create_or_extend(args, parser)
    elif args['subcommand'] == 'package':
        __casestudy_package(args, parser)
    elif args['subcommand'] == 'view':
        __casestudy_view(args, parser)


def __casestudy_status(args: tp.Dict[str, tp.Any],
                       parser: ArgumentParser) -> None:
    if 'paper_config' in args:
        CFG['paper_config']['current_config'] = args['paper_config']
    if args['short'] and args['list_revs']:
        parser.error(
            "At most one argument of: --short, --list-revs can be used.")
    if args['short'] and args['ws']:
        parser.error("At most one argument of: --short, --ws can be used.")
    PCM.show_status_of_case_studies(args['report_name'], args['filter_regex'],
                                    args['short'], args['sorted'],
                                    args['list_revs'], args['ws'],
                                    args['legend'])


def __casestudy_view(args: tp.Dict[str, tp.Any],
                     parser: ArgumentParser) -> None:

    # TODO replace prints with parser or matching loggers

    report_name = args['report_name']
    file_name = ""

    report = None  # TODO get report-object from name as string
    matches = find(CFG["result_dir"], "-name",
                   # f"CR-*-{args['commit_hash']}_success.yaml").split()
                   f"{report.SHORTHAND}-*-{args['commit_hash']}_success.{report.FILE_TYPE}")
    if not matches:
        parser.error("No result was found for this report and this revision.")
    elif len(matches) == 1:
        file_name = matches[0]
    # TODO limit amount of results or warn if more than 10 matches
    else:
        print("There are multiple matches. Please choose one:")
        for match in matches:
            print(f"{matches.index(match) + 1}: {match}")
        usr_input = ''
        while usr_input not in range(1, len(matches) + 1, 1):
            usr_input = int(input("Input: "))
            file_name = matches[usr_input - 1]

    # open the file in the default text editor or vi if none is set
    editor_name = os.getenv('EDITOR', 'vi')
    _tmp = __import__('benchbuild.utils.cmd', fromlist=[editor_name])
    editor = getattr(_tmp, editor_name)
    editor[file_name] & FG


def __casestudy_create_or_extend(args: tp.Dict[str, tp.Any],
                                 parser: ArgumentParser) -> None:
    if "project" not in args and "git_path" not in args:
        parser.error("need --project or --git-path")
        return

    if "project" in args and "git_path" not in args:
        args['git_path'] = str(get_local_project_git_path(args['project']))

    if "git_path" in args and "project" not in args:
        args['project'] = Path(args['git_path']).stem.replace("-HEAD", "")

    args['get_cmap'] = create_lazy_commit_map_loader(
        args['project'], args.get('cmap', None), args['end'],
        args['start'] if 'start' in args else None)
    cmap = args['get_cmap']()

    if args['subcommand'] == 'ext':
        case_study = load_case_study_from_file(Path(args['case_study_path']))

        # If no merge_stage was specified add it to the last
        if args['merge_stage'] == -1:
            args['merge_stage'] = max(case_study.num_stages - 1, 0)
        # If + was specified we add a new stage
        if args['merge_stage'] == '+':
            args['merge_stage'] = case_study.num_stages

        # Setup default result folder
        if 'result_folder' not in args and args[
                'strategy'] is ExtenderStrategy.smooth_plot:
            args['project'] = case_study.project_name
            args['result_folder'] = str(
                CFG['result_dir']) + "/" + args['project']
            LOG.info(f"Result folder defaults to: {args['result_folder']}")

        extend_case_study(case_study, cmap, args['strategy'], **args)

        store_case_study(case_study, Path(args['case_study_path']))
    else:
        args['paper_config_path'] = Path(args['paper_config_path'])
        if not args['paper_config_path'].exists():
            raise ArgumentTypeError("Paper path does not exist")

        # Specify merge_stage as 0 for creating new case studies
        args['merge_stage'] = 0

        case_study = generate_case_study(args['distribution'], cmap,
                                         args['version'], args['project'],
                                         **args)

        store_case_study(case_study, args['paper_config_path'])


def __casestudy_package(args: tp.Dict[str, tp.Any],
                        parser: ArgumentParser) -> None:
    output_path = Path(args["output"])
    if output_path.suffix == '':
        output_path = Path(str(output_path) + ".zip")
    if output_path.suffix == '.zip':
        vara_root = Path(str(CFG["config_file"])).parent
        if Path(os.getcwd()) != vara_root:
            LOG.info(f"Packaging needs to be called from VaRA root dir, "
                     f"changing dir to {vara_root}")
            os.chdir(vara_root)

        PCM.package_paper_config(output_path, re.compile(args['filter_regex']),
                                 args['report_names'])
    else:
        parser.error(
            "--output has the wrong file type extension. "
            "Please do not provide any other file type extension than .zip")


if __name__ == '__main__':
    main()
