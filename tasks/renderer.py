from invoke import task, Collection


@task
def create_stl(ctx, file):
    """ Parse and print brick project - `inv parse <path-to-entry-file>` """
    from parser import renderer

    result = renderer.create_stl(file)
    print(f'{result} created')


render_collection = Collection('render')
render_collection.add_task(create_stl, name="stl", default=True)
