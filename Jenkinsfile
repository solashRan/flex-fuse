ZARCHO_GIT = "git@github.com:${params.zarcho_user}/zarcho.git"
GITHUB_AUTH = 'github_auth_id'


library identifier: 'pipelinex@development', retriever: modernSCM(
    [$class: 'GitSCMSource',
     credentialsId: GITHUB_AUTH,
     remote: 'git@github.com:iguazio/pipelinex.git']) _


library identifier: "zarcho@${params.zarcho_branch}", retriever: modernSCM(
    [$class: 'GitSCMSource',
     credentialsId: GITHUB_AUTH,
     remote: ZARCHO_GIT]) _


builder.set_job_properties([
    string(defaultValue: 'REPLACE_ME', description: '', name: 'build_version'),
    string(defaultValue: 'development', description: '', name: 'flex_fuse_branch'),
    string(defaultValue: 'v3io', description: '', name: 'flex_fuse_user'),
    string(defaultValue: 'next', description: '', name: 'zarcho_branch'),
    string(defaultValue: 'iguazio', description: '', name: 'zarcho_user'),
    string(defaultValue: 'short', description: '', name: 'workflow'),
    text(defaultValue: libraryResource('default_snapshot.json'), description: '', name: 'snapshot'),
])


common.notify_slack {
    common.set_current_display_name(params.build_version)
    nodes.centos_node() {
        common.git_clone('zarcho', params.zarcho_user, params.zarcho_branch)
        stash name: 'zarcho'
    }

    throttle(['build']) {
        node('k8s-builder') {
            builder.build_flexfuse(params.build_version, params.snapshot, params.workflow)
        }
    }
}
