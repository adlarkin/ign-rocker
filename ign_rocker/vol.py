import em
import os
import pkgutil
from rocker.extensions import RockerExtension, name_to_argument


class Vol(RockerExtension):

    name = 'vol'

    @classmethod
    def get_name(cls):
        return cls.name

    def precondition_environment(self, cli_args):
        pass

    def validate_environment(self, cli_args):
        pass

    def get_preamble(self, cli_args):
        return ''

    def get_snippet(self, cli_args):
        return ''

    def get_docker_args(self, cli_args):
        args = ['']
        all_volumes = cli_args[Vol.get_name()].split('::')
        for volume in all_volumes:
            local, remote = volume.split(':')
            args.append('-v {0}:{1}'.format(local, remote))
        return ' '.join(args)

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(name_to_argument(Vol.get_name()),
            metavar='/LOCAL/PATH:/CONTAINER/PATH',
            default=defaults.get(Vol.get_name(), None),
            help="Mount files on your machine into the container via Docker volumes. When specifying local paths, absolute paths must be used. Multiple volumes can be passed in, but must be separated by '::'.")
