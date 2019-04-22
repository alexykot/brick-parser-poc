from invoke import task, Collection

from tasks import helpers


@task
def style(ctx, lint=False, style=False):
    """
        Check code style (--style), pylint (--lint) or both (default).
        Execute:
        `pycodestyle --config=pystyle.cfg ./service_auth/ `
        `pycodestyle --config=pystyle.cfg ./tests/ `
        `pylint ./service_auth/ `
        `pylint ./tests/ `
    """

    run_all = not style and not lint

    if style or run_all:
        ctx.run('pycodestyle --config=pystyle.cfg ./service_auth/ ', warn=True)
        ctx.run('pycodestyle --config=pystyle.cfg ./tests/ ', warn=True)
    if lint or run_all:
        ctx.run('pylint ./service_auth/', warn=True)
        ctx.run('pylint ./tests/', warn=True)

    helpers.send_notification('style check done')


@task
def types(ctx):
    """
    Run static typing check with MyPy.
    Execute `mypy --config-file ./.mypy service_auth/app.py`
    """

    ctx.run("mypy --config-file ./.mypy service_auth/app.py", warn=True)

    helpers.send_notification('typing check done')


@task
def tests_list(ctx):
    """ Get all test names
        if run from command - print tests names
        else return to parent method array ot test names
    """
    ctx.run('py.test --list')


@task
def run(ctx):
    """ Run all tests using pytest.
    """
    ctx.run('py.test')

    helpers.send_notification('tests.run done')


@task
def tests_all(ctx):
    """Run all checks at once."""

    style(ctx)
    types(ctx)
    run(ctx)


tests_collection = Collection('tests')
tests_collection.add_task(style)
tests_collection.add_task(types)
tests_collection.add_task(tests_list, name="list")
tests_collection.add_task(run)
tests_collection.add_task(tests_all, name="all", default=True)
