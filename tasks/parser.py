import yaml
from invoke import task, Collection


@task
def parse(ctx, file):
    """ Parse and print brick project - `inv parse <path-to-entry-file>` """
    from parser import parser

    result = parser.parse(file)
    print(f'{file} parsed')
    # print(yaml.dump(result))


parser_collection = Collection('parse')
parser_collection.add_task(parse, default=True)
