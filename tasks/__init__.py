import yaml
from invoke import task, Collection

from tasks.tests import tests_collection


ns = Collection()
ns.add_collection(tests_collection)


@task
def list(ctx):
    """ List all available tasks. """
    ctx.run('invoke --list')


@task
def parse(ctx, file):
    """ Parse and print brick project - `inv parse <path-to-entry-file>` """
    from parser import parser

    result = parser.parse(file)
    print(yaml.dump(result))


ns.add_task(list)
ns.add_task(parse)
