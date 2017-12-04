"""A script to generate a cloudbuild yaml."""

import os
import yaml

import util


# Add directories for new tests here.
TEST_DIRS = [
    'packages_test'
]

_ST_IMAGE = ('gcr.io/gcp-runtimes/structure-test:'
             '6195641f5a5a14c63c7945262066270842150ddb')
_TEST_DIR = '/workspace/ftl/python/testdata'
_PYTHON_BASE = 'gcr.io/google-appengine/python:latest'


def main():

    cloudbuild_yaml = util.INITIAL_CLOUDBUILD_YAML
    cloudbuild_yaml['steps'].append(
        # Build the FTL image from source and load it into the daemon.
        {
            'name': 'gcr.io/cloud-builders/bazel',
            'args': ['run', '//ftl:python_builder_image', '--', '--norun'],
            'id': 'build-builder',
            'waitFor': [cloudbuild_yaml['steps'][0]['id']],
        },
    )

    # Generate a set of steps for each test and add them.
    test_map = {}
    for test in TEST_DIRS:
        test_map[test] = [
            '--base', _PYTHON_BASE, '--name',
            'gcr.io/ftl-node-test/%s-image:latest' % test, '--directory',
            os.path.join(_TEST_DIR, test), '--no-cache'
        ]
    for test, args in test_map.iteritems():
        cloudbuild_yaml['steps'] += util.run_test_steps(
            'python_builder_image',
            'gcr.io/ftl-node-test/%s-image:latest' % test,
            os.path.join(_TEST_DIR, test),
            args)

    print yaml.dump(cloudbuild_yaml)


if __name__ == "__main__":
    main()