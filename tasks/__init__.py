from invoke import task, Collection

from tasks.tests import tests_collection
from tasks.parser import parser_collection
from tasks.renderer import render_collection


ns = Collection()
ns.add_collection(tests_collection)
ns.add_collection(parser_collection)
ns.add_collection(render_collection)


@task
def list_tasks(ctx):
    """ List all available tasks. """
    ctx.run('invoke --list')


ns.add_task(list_tasks, name="list")
