"""A case study is used to pin down the exact set of revisions that should be
analysed for a project."""

import typing as tp
from pathlib import Path

from varats.base.sampling_method import SamplingMethod
from varats.base.version_header import VersionHeader
from varats.provider.release.release_provider import ReleaseType
from varats.report.report import FileStatusExtension, MetaReport
from varats.utils.yaml_util import load_yaml, store_as_yaml


class HashIDTuple():
    """Combining a commit hash with a unique and ordered id, starting with 0 for
    the first commit in the repository."""

    def __init__(self, commit_hash: str, commit_id: int) -> None:
        self.__commit_hash = commit_hash
        self.__commit_id = commit_id

    @property
    def commit_hash(self) -> str:
        """A commit hash from the git repository."""
        return self.__commit_hash

    @property
    def commit_id(self) -> int:
        """The order ID of the commit hash."""
        return self.__commit_id

    def get_dict(self) -> tp.Dict[str, tp.Union[str, int]]:
        """Get a dict representation of this commit and id."""
        return dict(commit_hash=self.commit_hash, commit_id=self.commit_id)

    def __str(self) -> str:
        return "({commit_id}: #{commit_hash})"\
            .format(commit_hash=self.commit_hash,
                    commit_id=self.commit_id)

    def __repr__(self) -> str:
        return "({commit_id}: #{commit_hash})"\
            .format(commit_hash=self.commit_hash,
                    commit_id=self.commit_id)


class CSStage():
    """
    A stage in a case-study, i.e., a collection of revisions.

    Stages are used to separate revisions into groups.
    """

    def __init__(
        self,
        name: tp.Optional[str] = None,
        sampling_method: tp.Optional[SamplingMethod] = None,
        release_type: tp.Optional[ReleaseType] = None,
        revisions: tp.Optional[tp.List[HashIDTuple]] = None
    ) -> None:
        self.__name: tp.Optional[str] = name
        self.__sampling_method: tp.Optional[SamplingMethod] = sampling_method
        self.__release_type: tp.Optional[ReleaseType] = release_type
        self.__revisions: tp.List[HashIDTuple
                                 ] = revisions if revisions is not None else []

    @property
    def revisions(self) -> tp.List[str]:
        """Project revisions that are part of this case study."""
        return [x.commit_hash for x in self.__revisions]

    @property
    def name(self) -> tp.Optional[str]:
        """Name of the stage."""
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        """Setter for the name of the stage."""
        self.__name = name

    @property
    def sampling_method(self) -> tp.Optional[SamplingMethod]:
        """The sampling method used for this stage."""
        return self.__sampling_method

    @sampling_method.setter
    def sampling_method(self, sampling_method: SamplingMethod) -> None:
        """Setter for the sampling method of the stage."""
        self.__sampling_method = sampling_method

    @property
    def release_type(self) -> tp.Optional[ReleaseType]:
        """The sampling method used for this stage."""
        return self.__release_type

    @release_type.setter
    def release_type(self, release_type: ReleaseType) -> None:
        """Setter for the sampling method of the stage."""
        self.__release_type = release_type

    def has_revision(self, revision: str) -> bool:
        """
        Check if a revision is part of this case study.

        Args:
            revision: project revision to check

        Returns:
            ``True``, in case the revision is part of the case study,
            ``False`` otherwise.
        """
        for cs_revision in self.__revisions:
            if cs_revision.commit_hash.startswith(revision):
                return True

        return False

    def add_revision(self, revision: str, commit_id: int) -> None:
        """
        Add a new revision to this stage.

        Args:
            revision: to add
            commit_id: unique ID for ordering of commits
        """
        if not self.has_revision(revision):
            self.__revisions.append(HashIDTuple(revision, commit_id))

    def sort(self, reverse: bool = True) -> None:
        """Sort the revisions of the case study by commit ID inplace."""
        self.__revisions.sort(key=lambda x: x.commit_id, reverse=reverse)

    def get_dict(
        self
    ) -> tp.Dict[str, tp.Union[str, tp.List[tp.Dict[str, tp.Union[str, int]]]]]:
        """Get a dict representation of this stage."""
        stage_dict: tp.Dict[str,
                            tp.Union[str,
                                     tp.List[tp.Dict[str,
                                                     tp.Union[str,
                                                              int]]]]] = dict()
        if self.name is not None:
            stage_dict['name'] = self.name
        if self.sampling_method is not None:
            stage_dict['sampling_method'] = self.sampling_method.name
        if self.release_type is not None:
            stage_dict['release_type'] = self.release_type.name
        revision_list = [revision.get_dict() for revision in self.__revisions]
        stage_dict['revisions'] = revision_list
        return stage_dict


class CaseStudy():
    """
    A case study persists a set of revisions of a project to allow easy
    reevaluation.

    Stored values:
     - name of the related benchbuild.project
     - a set of revisions
    """

    def __init__(
        self,
        project_name: str,
        version: int,
        stages: tp.Optional[tp.List[CSStage]] = None
    ) -> None:
        self.__project_name = project_name
        self.__version = version
        self.__stages = stages if stages is not None else []

    @property
    def project_name(self) -> str:
        """
        Name of the related project.

        !! This name must match the name of the BB project !!
        """
        return self.__project_name

    @property
    def version(self) -> int:
        """
        Version ID for this case study.

        The version differentiates case studies of the same project.
        """
        return self.__version

    @property
    def revisions(self) -> tp.List[str]:
        """Project revisions that are part of this case study."""
        return list(
            dict.fromkeys([
                x for stage in self.__stages for x in stage.revisions
            ])
        )

    @property
    def stages(self) -> tp.List[CSStage]:
        """Get a list with all stages."""
        # Return new list to forbid modification of the case-study
        return list(self.__stages)

    @property
    def num_stages(self) -> int:
        """Get nummer of stages."""
        return len(self.__stages)

    def get_stage_by_name(self, stage_name: str) -> tp.Optional[CSStage]:
        """
        Get a stage by its name. Since multiple stages can have the same name,
        the first matching stage is returned.

        Args:
            stage_name: name of the stage to lookup

        Returns:
            the stage, corresponding with the 'stage_name', or ``None``
        """
        for stage in self.__stages:
            if stage.name == stage_name:
                return stage

        return None

    def get_stage_index_by_name(self, stage_name: str) -> tp.Optional[int]:
        """
        Get a stage's index by its name. Since multiple stages can have the same
        name, the first matching stage is returned.

        Args:
            stage_name: name of the stage to lookup

        Returns:
            the stage index, corresponding with the 'stage_name', or ``None``
        """
        for i in range(len(self.__stages)):
            if self.__stages[i].name == stage_name:
                return i

        return None

    def has_revision(self, revision: str) -> bool:
        """
        Check if a revision is part of this case study.

        Returns:
            ``True``, if the revision was found in one of the stages,
            ``False`` otherwise
        """
        for stage in self.__stages:
            if stage.has_revision(revision):
                return True

        return False

    def has_revision_in_stage(self, revision: str, num_stage: int) -> bool:
        """
        Checks if a revision is in a specific stage.

        Returns:
            ``True``, if the revision was found in the specified stage,
            ``False`` otherwise
        """
        if self.num_stages <= num_stage:
            return False
        return self.__stages[num_stage].has_revision(revision)

    def shift_stage(self, from_index: int, offset: int) -> None:
        """
        Shift a stage in the case-studie's stage list by an offset. Beware that
        shifts to the left (offset<0) will destroy stages.

        Args:
            from_index: index of the first stage to shift
            offset: amount to stages should be shifted
        """
        # keep parens for clarification
        if not (0 <= from_index < len(self.__stages)):  # pylint: disable=C0325
            raise AssertionError("from_index out of bounds")
        if (from_index + offset) < 0:
            raise AssertionError("Shifting out of bounds")

        if offset > 0:
            for _ in range(offset):
                self.__stages.insert(from_index, CSStage())

        if offset < 0:
            remove_index = from_index + offset
            for _ in range(abs(offset)):
                self.__stages.pop(remove_index)

    def insert_empty_stage(self, pos: int) -> CSStage:
        """
        Insert a new stage at the given index, shifting the list elements to the
        right. The newly created stage is returned.

        Args:
            pos: index position to insert an empty stage
        """
        new_stage = CSStage()
        self.__stages.insert(pos, new_stage)
        return new_stage

    def include_revision(
        self,
        revision: str,
        commit_id: int,
        stage_num: int = 0,
        sort_revs: bool = True
    ) -> None:
        """
        Add a revision to this case study.

        Args:
            revision: to add
            commit_id: unique ID for ordering of commits
            stage_num: index number of the stage to add the revision to
            sort_revs: if True, the modified stage will be sorted afterwards
        """
        # Create missing stages
        while self.num_stages <= stage_num:
            self.__stages.append(CSStage())

        stage = self.__stages[stage_num]

        if not stage.has_revision(revision):
            stage.add_revision(revision, commit_id)
            if sort_revs:
                stage.sort()

    def include_revisions(
        self,
        revisions: tp.List[tp.Tuple[str, int]],
        stage_num: int = 0,
        sort_revs: bool = True,
        sampling_method: tp.Optional[SamplingMethod] = None,
        release_type: tp.Optional[ReleaseType] = None
    ) -> None:
        """
        Add multiple revisions to this case study.

        Args:
            revisions: List of tuples with (commit_hash, id) to be inserted
            stage_num: The stage to insert the revisions
            sort_revs: True if the stage should be kept sorted
            sampling_method: The sampling method used to acquire the revisions
        """
        for revision in revisions:
            self.include_revision(revision[0], revision[1], stage_num, False)

        if len(self.__stages) <= stage_num:
            for idx in range(len(self.__stages), stage_num + 1):
                self.insert_empty_stage(idx)

        stage = self.__stages[stage_num]

        if sort_revs and self.num_stages > 0:
            self.__stages[stage_num].sort()

    def name_stage(self, stage_num: int, name: str) -> None:
        """
        Names an already existing stage.

        Args:
            stage_num: The number of the stage to name
            name: The new name of the stage
        """
        if stage_num < self.num_stages:
            self.__stages[stage_num].name = name

    def get_revision_filter(self) -> tp.Callable[[str], bool]:
        """
        Generate a case study specific revision filter that only allows revision
        that are part of the case study.

        Returns:
            a callable filter function
        """

        def revision_filter(revision: str) -> bool:
            return self.has_revision(revision)

        return revision_filter

    def get_dict(
        self
    ) -> tp.Dict[str, tp.Union[str, int, tp.List[tp.Dict[str, tp.Union[
        str, tp.List[tp.Dict[str, tp.Union[str, int]]]]]]]]:
        """Get a dict representation of this case study."""
        return dict(
            project_name=self.project_name,
            version=self.version,
            stages=[stage.get_dict() for stage in self.stages]
        )


def load_case_study_from_file(file_path: Path) -> CaseStudy:
    """
    Load a case study from a file.

    Args:
        file_path: path to the case study file
    """
    documents = load_yaml(file_path)
    version_header = VersionHeader(next(documents))
    version_header.raise_if_not_type("CaseStudy")
    version_header.raise_if_version_is_less_than(1)

    raw_case_study = next(documents)
    stages: tp.List[CSStage] = []
    for raw_stage in raw_case_study['stages']:
        hash_id_tuples: tp.List[HashIDTuple] = []
        for raw_hash_id_tuple in raw_stage['revisions']:
            hash_id_tuples.append(
                HashIDTuple(
                    raw_hash_id_tuple['commit_hash'],
                    raw_hash_id_tuple['commit_id']
                )
            )
        sampling_method = raw_stage.get('sampling_method') or None
        release_type = raw_stage.get('release_type') or None
        stages.append(
            CSStage(
                raw_stage.get('name') or None, SamplingMethod[sampling_method]
                if sampling_method is not None else None,
                ReleaseType[release_type] if release_type is not None else None,
                hash_id_tuples
            )
        )

    return CaseStudy(
        raw_case_study['project_name'], raw_case_study['version'], stages
    )


def store_case_study(case_study: CaseStudy, case_study_location: Path) -> None:
    """
    Store case study to file in the specified paper_config.

    Args:
        case_study: the case study to store
        case_study_location: can be either a path to a paper_config
                             or a direct path to a `.case_study` file
    """
    if case_study_location.suffix != '.case_study':
        file_name = "{project_name}_{version}.case_study".format(
            project_name=case_study.project_name, version=case_study.version
        )
        case_study_location /= file_name

    __store_case_study_to_file(case_study, case_study_location)


def __store_case_study_to_file(case_study: CaseStudy, file_path: Path) -> None:
    """Store case study to file."""
    store_as_yaml(
        file_path,
        [VersionHeader.from_version_number('CaseStudy', 1), case_study]
    )