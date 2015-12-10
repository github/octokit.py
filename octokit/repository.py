# -*- coding: utf-8 -*-


class Repository(object):
    def __parse_owner_repo(self, owner, repo):
        """Turns 'owner/repo' into ('owner', 'repo')."""
        if not repo:
            owner, repo = owner.split('/')
        return owner, repo

    def repository(self, owner, repo=None, **kwargs):
        """Get a single repository.

        https://developer.github.com/v3/repos/#get
        """
        owner, repo = self.__parse_owner_repo(owner, repo)
        print(type(super(Repository, self)))
        return super(Repository, self).repository(repo=repo, owner=owner,
                                                  **kwargs)

    repo = repository

    def edit_repository(self, owner, repo=None, **kwargs):
        """Edit a repository

        https://developer.github.com/v3/repos/#edit
        """
        repo = self.repository(owner, repo)
        repo.patch(kwargs)

    edit = edit_repository
    update_repository = edit_repository

    def repositories(self, user=None, **kwargs):
        """List user repositories.

        If user is not supplied, repositories for the current
        authenticated user are returned.

        https://developer.github.com/v3/repos/#list-your-repositories
        """
        user = self.user(user, **kwargs)
        return user.repos(**kwargs)

    list_repositories = repositories
    list_repos = repositories
    repos = repositories

    def all_repositories(self, **kwargs):
        """List all repositories.

        This provides a dump of every repository, in the order that they were
        created.

        https://developer.github.com/v3/repos/#list-all-public-repositories
        """
        raise NotImplementedError

    def star(self, owner, repo=None, **kwargs):
        owner, repo = self.__parse_owner_repo(owner, repo)
        return self.bool_from_response(
            lambda: self.starred.put(owner=owner, repo=repo, **kwargs))

    def unstar(self, owner, repo=None, **kwargs):
        owner, repo = self.__parse_owner_repo(owner, repo)
        return self.bool_from_response(
            lambda: self.starred.delete(owner=owner, repo=repo, **kwargs))
