import groovy.json.JsonOutput


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
])


common.notify_slack {
    common.set_current_display_name(params.build_version)

    stage('git clone') {
        nodes.centos_node() {
            common.git_clone('zarcho', params.zarcho_user, params.zarcho_branch)
            stash name: 'zarcho'
        }
    }

    stage('build images') {
        nodes.throttle_k8s_node('build') {
            def snapshot = ['k8s':
                                ['flex-fuse':
                                    ['branch': params.flex_fuse_branch,
                                     'git_url': "git@github.com:${params.flex_fuse_user}/flex-fuse.git",
                                    ]
                                ]
                           ]

            builder.build_flexfuse(params.build_version, JsonOutput.toJson(snapshot), params.workflow)
        }
    }
}
