from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from tron.config.schema import ConfigAction
from tron.config.schema import ConfigConstraint
from tron.config.schema import ConfigParameter
from tron.config.schema import ConfigVolume
from tron.core.action import Action


class TestAction:
    @pytest.mark.parametrize('disk', [600., None])
    def test_from_config_full(self, disk):
        config = ConfigAction(
            name="ted",
            command="do something",
            node="first",
            executor="ssh",
            cpus=1,
            mem=100,
            disk=disk,  # default: 1024.0
            constraints=[
                ConfigConstraint(
                    attribute='pool',
                    operator='LIKE',
                    value='default',
                ),
            ],
            docker_image='fake-docker.com:400/image',
            docker_parameters=[
                ConfigParameter(
                    key='test',
                    value=123,
                ),
            ],
            env={'TESTING': 'true'},
            extra_volumes=[
                ConfigVolume(
                    host_path='/tmp',
                    container_path='/nail/tmp',
                    mode='RO',
                ),
            ],
            trigger_downstreams=True,
            triggered_by=["foo.bar"],
        )
        new_action = Action.from_config(config)
        assert new_action.name == config.name
        assert new_action.node_pool is None
        assert new_action.executor == config.executor
        assert new_action.trigger_downstreams is True
        assert new_action.triggered_by == ['foo.bar']

        command_config = new_action.command_config
        assert command_config.command == config.command
        assert command_config.cpus == config.cpus
        assert command_config.mem == config.mem
        assert command_config.disk == (600. if disk else 1024.)
        assert command_config.constraints == {('pool', 'LIKE', 'default')}
        assert command_config.docker_image == config.docker_image
        assert command_config.docker_parameters == {('test', 123)}
        assert command_config.env == config.env
        assert command_config.extra_volumes == {('/nail/tmp', '/tmp', 'RO')}

    def test_from_config_none_values(self):
        config = ConfigAction(
            name="ted",
            command="do something",
            node="first",
            executor="ssh",
        )
        new_action = Action.from_config(config)
        assert new_action.name == config.name
        assert new_action.executor == config.executor
        command_config = new_action.command_config
        assert command_config.command == config.command
        assert command_config.constraints == set()
        assert command_config.docker_image is None
        assert command_config.docker_parameters == set()
        assert command_config.env == {}
        assert command_config.extra_volumes == set()
