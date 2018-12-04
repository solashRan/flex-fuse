import os

from twisted.internet import defer, task, reactor

import ziggy.utils
import ziggy.fs
import ziggy.tasks


def hook_on_module_load(project):
    base_path = os.path.join(project.config['workspace_path'], project.config['root_projects']['flex-fuse']['path'])

    flex_fuse_config = dict()
    flex_fuse_config['base_path'] = base_path
    flex_fuse_config['flex_fuse_path'] = os.path.join(base_path, 'flex-fuse')
    flex_fuse_config['scripts_path'] = os.path.join(base_path, 'scripts')
    flex_fuse_config['docker_path'] = os.path.join(base_path, 'docker')
    flex_fuse_config['repositories'] = {
        'flex-fuse': project.config['root_projects']['flex-fuse']
    }

    flex_fuse_config['zetup_path'] = os.path.join(flex_fuse_config['flex_fuse_path'], 'zetup.py')
    flex_fuse_config['zetup_md5'] = ziggy.fs.calculate_file_md5(project.ctx, flex_fuse_config['zetup_path'])

    project.config['flex-fuse'] = flex_fuse_config


@defer.inlineCallbacks
def task_wait_all_projects_updated(project):
    yield ziggy.tasks.wait_all_projects_updated(project)


@defer.inlineCallbacks
def task_declare_project_updated(project, zetup_path, old_zetup_md5):
    yield ziggy.tasks.declare_project_updated(project, zetup_path, old_zetup_md5)


@defer.inlineCallbacks
def task_update_sources(project):

    # update all branches tracking the upstream branch (e.g. if the upstream branch is 'development', merge
    # upstream/development -> development). specify that we want to check out the local branch
    yield ziggy.tasks.update_sources(project,
                                     repositories=project.config['flex-fuse']['repositories'],
                                     base_path=project.config['flex-fuse']['base_path'])


@defer.inlineCallbacks
def task_load_snapshot(project, repo_merges=None):
    yield ziggy.tasks.load_snapshot(project,
                                    project_path=project.config['root_projects']['flex-fuse']['path'],
                                    base_path=project.config['flex-fuse']['base_path'],
                                    repo_merges=repo_merges)


@defer.inlineCallbacks
def task_take_snapshot(project, filter=None):
    yield ziggy.tasks.take_snapshot(project,
                                    repositories=project.config['kubeops']['repositories'].keys(),
                                    project_path=project.config['root_projects']['flex-fuse']['path'],
                                    base_path=project.config['flex-fuse']['base_path'],
                                    filter=filter)


@defer.inlineCallbacks
def task_verify_zetup_unchanged(project):
    yield ziggy.tasks.wait_workspace_updated(project,
                                             project.config['flex-fuse']['zetup_path'],
                                             project.config['flex-fuse']['zetup_md5'])


@defer.inlineCallbacks
def task_workflow(project, skipped_tasks=None):
    skipped_tasks = ziggy.utils.as_list(skipped_tasks) or []

    # default workflow
    workflow_tasks = [
        'update_sources',
        'load_snapshot',
        'verify_zetup_unchanged',
        'take_snapshot'
    ]

    # Remove tasks we want to skip.
    workflow_tasks = project.task_manager.normalize_task_semantics(workflow_tasks)
    workflow_tasks = [task for task in workflow_tasks if task['name'] not in skipped_tasks]

    yield project.task_manager.run_tasks(project, workflow_tasks)
