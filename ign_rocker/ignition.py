import em
import pkgutil
import sys
from rocker.extensions import RockerExtension, name_to_argument


class Ignition(RockerExtension):
    @staticmethod
    def get_name():
        return 'ignition'

    @staticmethod
    def get_releases():
        return {'citadel', 'dome', 'edifice'}

    @staticmethod
    def get_OSs():
        return {'bionic', 'focal'}

    def __init__(self):
        self._env_subs = {}
        self.name = Ignition.get_name()

    def precondition_environment(self, cli_args):
        pass

    def validate_environment(self, cli_args):
        pass

    def get_preamble(self, cli_args):
        return ''

    def get_snippet(self, cli_args):
        ign_ver, linux_ver = cli_args[Ignition.get_name()].split(':')

        if (ign_ver not in Ignition.get_releases()):
            print("WARNING specified Ignition version '%s' is not valid, must choose from " % ign_ver, Ignition.get_releases())
            sys.exit(1)
        if (linux_ver not in Ignition.get_OSs()):
            print("WARNING specified OS '%s' is not valid, must choose from " % linux_ver, Ignition.get_OSs())
            sys.exit(1)

        self._env_subs['ign_distro'] = ign_ver
        self._env_subs['system_version'] = linux_ver
        snippet = pkgutil.get_data(
            'ign_rocker',
            'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        return em.expand(snippet, self._env_subs)

    def get_docker_args(self, cli_args):
        return ''

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(name_to_argument(Ignition.get_name()),
            default=defaults.get(Ignition.get_name(), None),
            metavar='$IGNITION_VERSION:$SYSTEM_VERSION',
            help="Install a specific version of the Ignition Robotics binary packages, along with the Ignition version's build dependencies for a particular platform. $IGNITION_VERSION must be either %s, and $SYSTEM_VERSION must be either %s. $SYSTEM_VERSION should match the base image being used." % (Ignition.get_releases(), Ignition.get_OSs()))
