from invoke import task, Collection


@task
def create_stl(ctx, file):
    """ copypaste STL 8 times into new STL - `inv stl <path-to-stl-file>` """
    from parser import composer

    result = composer.create_stl(file)
    print(f'{result} created')


@task
def convert_to_ascii(ctx, file):
    """ Convert STL to ASCII - `inv ascii <path-to-stl-file>` """
    from parser import composer

    result = composer.create_ascii(file)
    print(f'{result} created')


render_collection = Collection('render')
render_collection.add_task(create_stl, name="stl", default=True)
render_collection.add_task(convert_to_ascii, name="ascii")
