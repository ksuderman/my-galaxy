from ..base.twilltestcase import (
    common,
    ShedTwillTestCase,
)

freebayes_repository_name = "freebayes_0040"
freebayes_repository_description = "Galaxy's freebayes tool for test 0040"
freebayes_repository_long_description = "Long description of Galaxy's freebayes tool for test 0040"

filtering_repository_name = "filtering_0040"
filtering_repository_description = "Galaxy's filtering tool for test 0040"
filtering_repository_long_description = "Long description of Galaxy's filtering tool for test 0040"


class TestRepositoryCircularDependencies(ShedTwillTestCase):
    """Verify that the code correctly displays repositories with circular repository dependencies."""

    def test_0000_initiate_users(self):
        """Create necessary user accounts."""
        self.login(email=common.test_user_1_email, username=common.test_user_1_name)
        test_user_1 = self.test_db_util.get_user(common.test_user_1_email)
        assert (
            test_user_1 is not None
        ), f"Problem retrieving user with email {common.test_user_1_email} from the database"
        self.test_db_util.get_private_role(test_user_1)
        self.login(email=common.admin_email, username=common.admin_username)
        admin_user = self.test_db_util.get_user(common.admin_email)
        assert admin_user is not None, f"Problem retrieving user with email {common.admin_email} from the database"
        self.test_db_util.get_private_role(admin_user)

    def test_0005_create_category(self):
        """Create a category for this test suite"""
        self.create_category(
            name="test_0040_repository_circular_dependencies",
            description="Testing handling of circular repository dependencies.",
        )

    def test_0010_create_freebayes_repository(self):
        """Create and populate freebayes_0040."""
        self.login(email=common.test_user_1_email, username=common.test_user_1_name)
        repository = self.get_or_create_repository(
            name=freebayes_repository_name,
            description=freebayes_repository_description,
            long_description=freebayes_repository_long_description,
            owner=common.test_user_1_name,
            categories=["test_0040_repository_circular_dependencies"],
            strings_displayed=[],
        )
        self.upload_file(
            repository,
            filename="freebayes/freebayes.tar",
            filepath=None,
            valid_tools_only=True,
            uncompress_file=True,
            remove_repo_files_not_in_tar=False,
            commit_message="Uploaded the tool tarball.",
            strings_displayed=[],
            strings_not_displayed=[],
        )

    def test_0015_create_filtering_repository(self):
        """Create and populate filtering_0040."""
        self.login(email=common.test_user_1_email, username=common.test_user_1_name)
        repository = self.get_or_create_repository(
            name=filtering_repository_name,
            description=filtering_repository_description,
            long_description=filtering_repository_long_description,
            owner=common.test_user_1_name,
            categories=["test_0040_repository_circular_dependencies"],
            strings_displayed=[],
        )
        self.upload_file(
            repository,
            filename="filtering/filtering_1.1.0.tar",
            filepath=None,
            valid_tools_only=True,
            uncompress_file=True,
            remove_repo_files_not_in_tar=False,
            commit_message="Uploaded the tool tarball for filtering 1.1.0.",
            strings_displayed=[],
            strings_not_displayed=[],
        )

    def test_0020_create_dependency_on_freebayes(self):
        """Upload a repository_dependencies.xml file that specifies the current revision of freebayes to the filtering_0040 repository."""
        # The dependency structure should look like:
        # Filtering revision 0 -> freebayes revision 0.
        # Freebayes revision 0 -> filtering revision 1.
        # Filtering will have two revisions, one with just the filtering tool, and one with the filtering tool and a dependency on freebayes.
        repository = self.test_db_util.get_repository_by_name_and_owner(
            freebayes_repository_name, common.test_user_1_name
        )
        filtering_repository = self.test_db_util.get_repository_by_name_and_owner(
            filtering_repository_name, common.test_user_1_name
        )
        repository_dependencies_path = self.generate_temp_path("test_0040", additional_paths=["filtering"])
        repository_tuple = (self.url, repository.name, repository.user.username, self.get_repository_tip(repository))
        self.create_repository_dependency(
            repository=filtering_repository, repository_tuples=[repository_tuple], filepath=repository_dependencies_path
        )

    def test_0025_create_dependency_on_filtering(self):
        """Upload a repository_dependencies.xml file that specifies the current revision of filtering to the freebayes_0040 repository."""
        # The dependency structure should look like:
        # Filtering revision 0 -> freebayes revision 0.
        # Freebayes revision 0 -> filtering revision 1.
        # Filtering will have two revisions, one with just the filtering tool, and one with the filtering tool and a dependency on freebayes.
        repository = self.test_db_util.get_repository_by_name_and_owner(
            filtering_repository_name, common.test_user_1_name
        )
        freebayes_repository = self.test_db_util.get_repository_by_name_and_owner(
            freebayes_repository_name, common.test_user_1_name
        )
        repository_dependencies_path = self.generate_temp_path("test_0040", additional_paths=["freebayes"])
        repository_tuple = (self.url, repository.name, repository.user.username, self.get_repository_tip(repository))
        self.create_repository_dependency(
            repository=freebayes_repository, repository_tuples=[repository_tuple], filepath=repository_dependencies_path
        )

    def test_0030_verify_repository_dependencies(self):
        """Verify that each repository can depend on the other without causing an infinite loop."""
        filtering_repository = self.test_db_util.get_repository_by_name_and_owner(
            filtering_repository_name, common.test_user_1_name
        )
        freebayes_repository = self.test_db_util.get_repository_by_name_and_owner(
            freebayes_repository_name, common.test_user_1_name
        )
        # The dependency structure should look like:
        # Filtering revision 0 -> freebayes revision 0.
        # Freebayes revision 0 -> filtering revision 1.
        # Filtering will have two revisions, one with just the filtering tool, and one with the filtering tool and a dependency on freebayes.
        # In this case, the displayed dependency will specify the tip revision, but this will not always be the case.
        self.check_repository_dependency(
            filtering_repository, freebayes_repository, self.get_repository_tip(freebayes_repository)
        )
        self.check_repository_dependency(
            freebayes_repository, filtering_repository, self.get_repository_tip(filtering_repository)
        )

    def test_0035_verify_repository_metadata(self):
        """Verify that resetting the metadata does not change it."""
        freebayes_repository = self.test_db_util.get_repository_by_name_and_owner(
            freebayes_repository_name, common.test_user_1_name
        )
        filtering_repository = self.test_db_util.get_repository_by_name_and_owner(
            filtering_repository_name, common.test_user_1_name
        )
        for repository in [freebayes_repository, filtering_repository]:
            self.verify_unchanged_repository_metadata(repository)

    def test_0040_verify_tool_dependencies(self):
        """Verify that freebayes displays tool dependencies."""
        repository = self.test_db_util.get_repository_by_name_and_owner(
            freebayes_repository_name, common.test_user_1_name
        )
        self.display_manage_repository_page(
            repository,
            strings_displayed=["freebayes", "0.9.4_9696d0ce8a9", "samtools", "0.1.18", "Valid tools", "package"],
            strings_not_displayed=["Invalid tools"],
        )
