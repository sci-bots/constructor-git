import os

import git
import path_helpers as ph

from . import CRE_DESCRIBE, build_miniconda_exe


def main(repo_root):
    repo_root = ph.path(repo_root).realpath()
    output_dir = ph.path(os.getcwd()).realpath()
    try:
        os.chdir(repo_root)
        repo = git.repo.Repo()
        describe_match = CRE_DESCRIBE.match(repo.git.describe(['--tags',
                                                               '--dirty']))

        build_miniconda_exe('.miniconda-recipe', output_dir,
                            context=describe_match.groupdict())
    finally:
        os.chdir(output_dir)


if __name__ == '__main__':
    main(os.getcwd())
